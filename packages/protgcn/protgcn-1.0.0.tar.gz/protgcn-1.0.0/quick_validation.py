#!/usr/bin/env python3
"""
Quick GCNdesign Validation Metrics
Simple script to get validation metrics for individual proteins
"""

import sys
import torch
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, matthews_corrcoef

# Add gcndesign to path
sys.path.append('.')
from gcndesign.predictor import Predictor
from gcndesign.hypara import HyperParam
from gcndesign.dataset import pdb2input

def get_validation_metrics(pdb_file, device='cpu'):
    """Get comprehensive validation metrics for a single protein"""
    print(f"🧬 Analyzing {pdb_file}...")
    
    # Initialize predictor and hyperparameters
    predictor = Predictor(device=device)
    hypara = HyperParam()
    
    try:
        # Get predictions
        predictions = predictor.predict_logit_tensor(pdb_file)
        pred_probs = torch.softmax(torch.tensor(predictions), dim=1).numpy()
        
        # Get ground truth
        node, edgemat, adjmat, labels, mask, aa_sequence = pdb2input(pdb_file, hypara)
        
        # Filter valid residues
        valid_mask = mask.numpy()
        true_labels = labels.numpy()[valid_mask]
        pred_labels = np.argmax(predictions, axis=1)[valid_mask]
        pred_probs_valid = pred_probs[valid_mask]
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, pred_labels)
        precision = precision_score(true_labels, pred_labels, average='macro', zero_division=0)
        recall = recall_score(true_labels, pred_labels, average='macro', zero_division=0)
        f1 = f1_score(true_labels, pred_labels, average='macro', zero_division=0)
        
        try:
            mcc = matthews_corrcoef(true_labels, pred_labels)
        except:
            mcc = 0.0
        
        # Top-k accuracy (manual calculation)
        top3_correct = 0
        top5_correct = 0
        for i, true_label in enumerate(true_labels):
            top3_preds = np.argsort(pred_probs_valid[i])[-3:]
            top5_preds = np.argsort(pred_probs_valid[i])[-5:]
            if true_label in top3_preds:
                top3_correct += 1
            if true_label in top5_preds:
                top5_correct += 1
        top3_acc = top3_correct / len(true_labels)
        top5_acc = top5_correct / len(true_labels)
        
        # Confidence analysis
        max_probs = np.max(pred_probs_valid, axis=1)
        avg_confidence = np.mean(max_probs)
        
        # Per-residue analysis
        correct_predictions = np.sum(true_labels == pred_labels)
        per_residue_acc = correct_predictions / len(true_labels)
        
        # Print results
        print(f"\n📊 VALIDATION METRICS for {pdb_file}:")
        print("=" * 60)
        print(f"   Total residues: {len(true_labels)}")
        print(f"   Correct predictions: {correct_predictions}")
        print(f"   Per-residue accuracy: {per_residue_acc:.4f} ({per_residue_acc*100:.2f}%)")
        print(f"\n   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1-Score:  {f1:.4f}")
        print(f"   MCC:       {mcc:.4f}")
        print(f"\n   Top-3 Accuracy: {top3_acc:.4f} ({top3_acc*100:.2f}%)")
        print(f"   Top-5 Accuracy: {top5_acc:.4f} ({top5_acc*100:.2f}%)")
        print(f"   Avg Confidence: {avg_confidence:.4f}")
        
        # Performance assessment
        if accuracy > 0.8:
            performance = "EXCELLENT"
        elif accuracy > 0.6:
            performance = "GOOD"
        elif accuracy > 0.4:
            performance = "MODERATE"
        else:
            performance = "NEEDS IMPROVEMENT"
        
        print(f"\n🏅 PERFORMANCE ASSESSMENT:")
        print(f"   Level: {performance}")
        print(f"   Overall: {accuracy*100:.1f}% accuracy")
        
        if top3_acc > 0.7:
            print(f"   ✓ Top-3 accuracy > 70% - Good for protein design")
        
        if avg_confidence > 0.5:
            print(f"   ✓ Average confidence > 50% - Model shows certainty")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'mcc': mcc,
            'top3_accuracy': top3_acc,
            'top5_accuracy': top5_acc,
            'avg_confidence': avg_confidence,
            'total_residues': len(true_labels),
            'correct_predictions': correct_predictions
        }
        
    except Exception as e:
        print(f"❌ Error analyzing {pdb_file}: {e}")
        return None

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick GCNdesign validation metrics')
    parser.add_argument('pdb_file', help='PDB file to analyze')
    parser.add_argument('--device', default='cpu', choices=['cpu', 'cuda'], 
                       help='Device to use (default: cpu)')
    
    args = parser.parse_args()
    
    # Get metrics
    metrics = get_validation_metrics(args.pdb_file, args.device)
    
    if metrics:
        print(f"\n✅ Analysis complete!")
    else:
        print(f"\n❌ Analysis failed!")

if __name__ == "__main__":
    main()
