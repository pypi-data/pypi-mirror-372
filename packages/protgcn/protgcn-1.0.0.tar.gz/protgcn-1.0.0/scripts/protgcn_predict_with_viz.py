#!/usr/bin/env python
"""
Enhanced ProtGCN Prediction Script with Visualization
Generates predictions and comprehensive visual analysis
"""

import sys
from os import path
import argparse
import torch

dir_script = path.dirname(path.realpath(__file__))
sys.path.append(dir_script+'/../')
from gcndesign.predictor import Predictor
from gcndesign.hypara import HyperParam
from gcndesign.dataset import pdb2input
from visualization import ProtGCNVisualizer

# default processing device
device = "cuda" if torch.cuda.is_available() else "cpu"

# argument parser
parser = argparse.ArgumentParser()
parser.add_argument('pdb', type=str, default=None, metavar='[File]',
                    help='PDB file input.')
parser.add_argument('--temperature', '-t', type=float, default=1.0, metavar='[Float]',
                    help='Temperature: probability P(AA) is proportional to exp(logit(AA)/T). (default:{})'.format(1.0))
parser.add_argument('--param-in', '-p', type=str, default=None, metavar='[File]',
                    help='NN parameter file. (default:{})'.format(None))
parser.add_argument('--device', type=str, default=device, choices=['cpu', 'cuda'],
                    help='Processing device. (default:\'cuda\' if available)')
parser.add_argument('--visualize', '-v', action='store_true',
                    help='Generate comprehensive visualizations')
parser.add_argument('--output-dir', '-o', type=str, default='predictions',
                    help='Output directory for visualizations (default: predictions)')
args = parser.parse_args()

# check files
assert path.isfile(args.pdb), "PDB file {:s} was not found.".format(args.pdb)

def format_prediction_results(pred_results, pdb_file):
    """Format prediction results for visualization"""
    results = []
    hypara = HyperParam()
    
    try:
        # Get ground truth for comparison
        node, edgemat, adjmat, labels, mask, aa_sequence = pdb2input(pdb_file, hypara)
        ground_truth_available = True
    except:
        ground_truth_available = False
        aa_sequence = None
    
    correct_predictions = 0
    
    for i, (prob_dict, info) in enumerate(pred_results):
        # Get top 5 predictions
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get original amino acid from ground truth if available
        original_aa = aa_sequence[i] if ground_truth_available and i < len(aa_sequence) else 'X'
        
        # Check if prediction is correct
        if original_aa != 'X' and sorted_probs[0][0] == original_aa:
            correct_predictions += 1
        
        results.append({
            'position': int(info['resnum']),
            'chain': str(info['chain']),
            'original': str(original_aa),
            'predicted': str(sorted_probs[0][0]),
            'confidence': float(sorted_probs[0][1]),
            'top_predictions': [
                {
                    'amino_acid': str(aa),
                    'probability': float(prob),
                    'percentage': float(prob * 100)
                }
                for aa, prob in sorted_probs
            ]
        })
    
    # Calculate summary statistics
    total_residues = len(results)
    accuracy = correct_predictions / total_residues if total_residues > 0 and ground_truth_available else None
    avg_confidence = sum([r['confidence'] for r in results]) / len(results)
    
    # Get protein sequences
    predicted_sequence = ''.join([r['predicted'] for r in results])
    original_sequence = ''.join([r['original'] for r in results]) if ground_truth_available else None
    
    summary = {
        'total_residues': int(total_residues),
        'correct_predictions': int(correct_predictions) if ground_truth_available else None,
        'accuracy': float(accuracy) if accuracy is not None else None,
        'avg_confidence': float(avg_confidence),
        'predicted_sequence': str(predicted_sequence),
        'original_sequence': str(original_sequence) if original_sequence else None,
        'ground_truth_available': bool(ground_truth_available)
    }
    
    return results, summary

# prediction
print(f"🧬 Starting ProtGCN prediction for {args.pdb}")
print(f"🔧 Device: {args.device}, Temperature: {args.temperature}")

predictor = Predictor(device=args.device, param=args.param_in)
pred = predictor.predict(pdb=args.pdb, temperature=args.temperature)

print(f"\n📊 PREDICTION RESULTS:")
print("="*80)

# Display terminal output
for pdict, info in pred:
    max_key = max(pdict, key=pdict.get)
    print(' %4d %s %s:pred ' % (info['resnum'], info['original'], max_key), end='')
    for aa in sorted(pdict.keys(), key=lambda x: pdict[x], reverse=True)[:5]:
        print(' %5.3f:%s' % (pdict[aa], aa), end='')
    print('')

# Generate visualizations if requested
if args.visualize:
    print(f"\n🎨 Generating visualizations...")
    
    # Format results for visualization
    results, summary = format_prediction_results(pred, args.pdb)
    
    # Initialize visualizer
    visualizer = ProtGCNVisualizer(save_dir=args.output_dir)
    
    # Get protein name from file
    protein_name = path.splitext(path.basename(args.pdb))[0]
    
    # Generate all visualizations
    generated_files = visualizer.generate_all_visualizations(results, summary, protein_name)
    
    print(f"\n✅ Visualization complete!")
    print(f"📁 Files saved in: {args.output_dir}/")
    
    # Display summary
    print(f"\n📈 PREDICTION SUMMARY:")
    print(f"   Total residues: {summary['total_residues']}")
    print(f"   Average confidence: {summary['avg_confidence']*100:.2f}%")
    print(f"   Predicted sequence: {summary['predicted_sequence']}")
    if summary['original_sequence']:
        print(f"   Original sequence:  {summary['original_sequence']}")

print(f"\n🎯 Prediction completed!")
if args.visualize:
    print(f"📊 Check the '{args.output_dir}' folder for detailed visual analysis!")
else:
    print(f"💡 Add --visualize flag to generate comprehensive charts and graphs!")
