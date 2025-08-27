#!/usr/bin/env python3
"""
ProtGCN Visualization Module
Generates comprehensive graphs and charts for protein sequence predictions
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import base64
from io import BytesIO

# Set up matplotlib for better rendering
plt.style.use('default')
sns.set_palette("husl")

class ProtGCNVisualizer:
    def __init__(self, save_dir="predictions"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Color schemes
        self.colors = {
            'original': '#2E86AB',      # Blue
            'predicted': '#A23B72',     # Purple
            'correct': '#2E8B57',       # Green
            'incorrect': '#DC143C',     # Red
            'confidence': '#F18F01',    # Orange
            'background': '#F8F9FA',    # Light gray
            'watermark': '#6C757D'      # Gray
        }
        
        # Amino acid properties for coloring
        self.aa_properties = {
            'A': 'nonpolar', 'V': 'nonpolar', 'L': 'nonpolar', 'I': 'nonpolar', 'M': 'nonpolar',
            'F': 'nonpolar', 'W': 'nonpolar', 'P': 'nonpolar', 'G': 'nonpolar',
            'S': 'polar', 'T': 'polar', 'C': 'polar', 'Y': 'polar', 'N': 'polar', 'Q': 'polar',
            'D': 'acidic', 'E': 'acidic',
            'K': 'basic', 'R': 'basic', 'H': 'basic'
        }
        
        self.property_colors = {
            'nonpolar': '#FFA500',  # Orange
            'polar': '#4169E1',     # Royal Blue  
            'acidic': '#DC143C',    # Crimson
            'basic': '#228B22'      # Forest Green
        }

    def add_watermark(self, ax, position='bottom-right'):
        """Add ProtGCN watermark to the plot"""
        if position == 'bottom-right':
            ax.text(0.98, 0.02, 'ProtGCN', transform=ax.transAxes, 
                   fontsize=10, alpha=0.7, ha='right', va='bottom',
                   color=self.colors['watermark'], weight='bold')
        elif position == 'bottom-left':
            ax.text(0.02, 0.02, 'ProtGCN', transform=ax.transAxes,
                   fontsize=10, alpha=0.7, ha='left', va='bottom',
                   color=self.colors['watermark'], weight='bold')

    def create_sequence_comparison_chart(self, original_seq, predicted_seq, confidence_scores, 
                                       protein_name, save_path=None):
        """Create a detailed sequence comparison chart"""
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12))
        fig.suptitle(f'ProtGCN Sequence Prediction Analysis: {protein_name}', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        positions = range(1, len(original_seq) + 1)
        correct_mask = np.array([o == p for o, p in zip(original_seq, predicted_seq)])
        
        # 1. Sequence Comparison Bar Chart
        ax1.bar(positions, [1]*len(positions), 
               color=[self.colors['correct'] if correct else self.colors['incorrect'] 
                     for correct in correct_mask],
               alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Add amino acid labels
        for i, (orig, pred) in enumerate(zip(original_seq, predicted_seq)):
            ax1.text(i+1, 0.5, f'{orig}\n{pred}', ha='center', va='center', 
                    fontsize=8, fontweight='bold',
                    color='white' if correct_mask[i] else 'black')
        
        ax1.set_xlabel('Residue Position')
        ax1.set_ylabel('Prediction Match')
        ax1.set_title('Sequence Comparison: Original (Top) vs Predicted (Bottom)')
        ax1.set_ylim(0, 1.2)
        ax1.grid(True, alpha=0.3)
        self.add_watermark(ax1)
        
        # 2. Confidence Scores
        bars = ax2.bar(positions, confidence_scores, 
                      color=[self.colors['correct'] if conf > 0.7 else 
                            self.colors['confidence'] if conf > 0.5 else 
                            self.colors['incorrect'] for conf in confidence_scores],
                      alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='50% Threshold')
        ax2.axhline(y=0.7, color='green', linestyle='--', alpha=0.7, label='70% Threshold')
        ax2.set_xlabel('Residue Position')
        ax2.set_ylabel('Prediction Confidence')
        ax2.set_title('Per-Residue Prediction Confidence')
        ax2.set_ylim(0, 1)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        self.add_watermark(ax2)
        
        # 3. Amino Acid Property Comparison
        orig_props = [self.aa_properties.get(aa, 'unknown') for aa in original_seq]
        pred_props = [self.aa_properties.get(aa, 'unknown') for aa in predicted_seq]
        
        # Create stacked bars for properties
        y_offset = 0.1
        for i, (orig_prop, pred_prop) in enumerate(zip(orig_props, pred_props)):
            # Original sequence (bottom)
            ax3.bar(i+1, 0.4, bottom=0, 
                   color=self.property_colors.get(orig_prop, 'gray'),
                   alpha=0.8, edgecolor='black', linewidth=0.5)
            # Predicted sequence (top)
            ax3.bar(i+1, 0.4, bottom=0.5,
                   color=self.property_colors.get(pred_prop, 'gray'),
                   alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax3.set_xlabel('Residue Position')
        ax3.set_ylabel('Amino Acid Properties')
        ax3.set_title('Amino Acid Property Comparison (Bottom: Original, Top: Predicted)')
        ax3.set_ylim(0, 1)
        ax3.set_yticks([0.2, 0.7])
        ax3.set_yticklabels(['Original', 'Predicted'])
        
        # Create legend for properties
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.8, label=prop.title()) 
                          for prop, color in self.property_colors.items()]
        ax3.legend(handles=legend_elements, loc='upper right')
        ax3.grid(True, alpha=0.3)
        self.add_watermark(ax3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Sequence comparison chart saved: {save_path}")
        
        return fig

    def create_accuracy_summary_chart(self, results_dict, protein_name, save_path=None):
        """Create summary accuracy and statistics chart"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'ProtGCN Prediction Summary: {protein_name}', 
                    fontsize=16, fontweight='bold')
        
        # 1. Overall Accuracy Pie Chart
        correct = results_dict.get('correct_predictions', 0)
        total = results_dict.get('total_residues', 1)
        incorrect = total - correct
        
        labels = ['Correct Predictions', 'Incorrect Predictions']
        sizes = [correct, incorrect]
        colors = [self.colors['correct'], self.colors['incorrect']]
        
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 10})
        ax1.set_title(f'Overall Accuracy\n({correct}/{total} residues)')
        self.add_watermark(ax1)
        
        # 2. Confidence Distribution
        confidences = results_dict.get('confidence_scores', [])
        ax2.hist(confidences, bins=20, color=self.colors['confidence'], alpha=0.7, 
                edgecolor='black', linewidth=0.5)
        ax2.axvline(np.mean(confidences), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(confidences):.3f}')
        ax2.set_xlabel('Prediction Confidence')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Confidence Score Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        self.add_watermark(ax2)
        
        # 3. Amino Acid Frequency Comparison
        amino_acids = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L',
                      'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']
        
        original_seq = results_dict.get('original_sequence', '')
        predicted_seq = results_dict.get('predicted_sequence', '')
        
        orig_counts = [original_seq.count(aa) for aa in amino_acids]
        pred_counts = [predicted_seq.count(aa) for aa in amino_acids]
        
        x = np.arange(len(amino_acids))
        width = 0.35
        
        ax3.bar(x - width/2, orig_counts, width, label='Original', 
               color=self.colors['original'], alpha=0.8)
        ax3.bar(x + width/2, pred_counts, width, label='Predicted',
               color=self.colors['predicted'], alpha=0.8)
        
        ax3.set_xlabel('Amino Acid')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Amino Acid Composition Comparison')
        ax3.set_xticks(x)
        ax3.set_xticklabels(amino_acids)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        self.add_watermark(ax3)
        
        # 4. Performance Metrics
        metrics_data = {
            'Accuracy': results_dict.get('accuracy', 0) * 100,
            'Avg Confidence': results_dict.get('avg_confidence', 0) * 100,
            'High Conf (>70%)': len([c for c in confidences if c > 0.7]) / len(confidences) * 100 if confidences else 0,
            'Low Conf (<50%)': len([c for c in confidences if c < 0.5]) / len(confidences) * 100 if confidences else 0
        }
        
        bars = ax4.bar(metrics_data.keys(), metrics_data.values(), 
                      color=[self.colors['correct'], self.colors['confidence'], 
                            self.colors['original'], self.colors['incorrect']],
                      alpha=0.8, edgecolor='black', linewidth=0.5)
        
        for bar, value in zip(bars, metrics_data.values()):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax4.set_ylabel('Percentage (%)')
        ax4.set_title('Performance Metrics Summary')
        ax4.set_ylim(0, 100)
        ax4.grid(True, alpha=0.3)
        plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')
        self.add_watermark(ax4)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Accuracy summary chart saved: {save_path}")
        
        return fig

    def create_confidence_heatmap(self, results, protein_name, save_path=None):
        """Create a heatmap showing confidence scores across the sequence"""
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Prepare data for heatmap
        positions = [r['position'] for r in results]
        amino_acids = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L',
                      'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']
        
        # Create matrix for heatmap
        heatmap_data = np.zeros((len(amino_acids), len(positions)))
        
        for i, result in enumerate(results):
            for pred in result['top_predictions']:
                aa_idx = amino_acids.index(pred['amino_acid'])
                heatmap_data[aa_idx, i] = pred['probability']
        
        # Create heatmap
        sns.heatmap(heatmap_data, 
                   xticklabels=[f"{pos}\n{results[i]['original']}\n{results[i]['predicted']}" 
                               for i, pos in enumerate(positions)],
                   yticklabels=amino_acids,
                   cmap='YlOrRd', 
                   cbar_kws={'label': 'Prediction Probability'},
                   ax=ax)
        
        ax.set_xlabel('Position (Original/Predicted)')
        ax.set_ylabel('Amino Acid')
        ax.set_title(f'Prediction Confidence Heatmap: {protein_name}')
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=90, ha='center', fontsize=8)
        
        self.add_watermark(ax)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Confidence heatmap saved: {save_path}")
        
        return fig

    def generate_all_visualizations(self, results, summary, protein_name):
        """Generate all visualization types and save them"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{protein_name}_{timestamp}"
        
        # Extract data
        original_seq = summary.get('original_sequence', '')
        predicted_seq = summary.get('predicted_sequence', '')
        confidence_scores = [r['confidence'] for r in results]
        
        generated_files = []
        
        if original_seq and predicted_seq:
            # 1. Sequence Comparison Chart
            comparison_path = self.save_dir / f"{base_name}_sequence_comparison.png"
            self.create_sequence_comparison_chart(
                original_seq, predicted_seq, confidence_scores, 
                protein_name, comparison_path
            )
            generated_files.append(comparison_path)
        
        # 2. Accuracy Summary Chart  
        summary_path = self.save_dir / f"{base_name}_accuracy_summary.png"
        results_dict = {
            'correct_predictions': summary.get('correct_predictions', 0),
            'total_residues': summary.get('total_residues', 0),
            'accuracy': summary.get('accuracy', 0),
            'avg_confidence': summary.get('avg_confidence', 0),
            'confidence_scores': confidence_scores,
            'original_sequence': original_seq,
            'predicted_sequence': predicted_seq
        }
        self.create_accuracy_summary_chart(results_dict, protein_name, summary_path)
        generated_files.append(summary_path)
        
        # 3. Confidence Heatmap
        heatmap_path = self.save_dir / f"{base_name}_confidence_heatmap.png"
        self.create_confidence_heatmap(results, protein_name, heatmap_path)
        generated_files.append(heatmap_path)
        
        print(f"\n📊 Generated {len(generated_files)} visualization files:")
        for file_path in generated_files:
            print(f"   ✓ {file_path}")
        
        return generated_files

    def fig_to_base64(self, fig):
        """Convert matplotlib figure to base64 string for web display"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)  # Close figure to free memory
        return image_base64

    def generate_web_visualizations(self, results, summary, protein_name):
        """Generate visualizations for web interface (returns base64 encoded images)"""
        # Extract data
        original_seq = summary.get('original_sequence', '')
        predicted_seq = summary.get('predicted_sequence', '')
        confidence_scores = [r['confidence'] for r in results]
        
        web_images = {}
        
        if original_seq and predicted_seq:
            # 1. Sequence Comparison Chart
            fig1 = self.create_sequence_comparison_chart(
                original_seq, predicted_seq, confidence_scores, protein_name
            )
            web_images['sequence_comparison'] = self.fig_to_base64(fig1)
        
        # 2. Accuracy Summary Chart
        results_dict = {
            'correct_predictions': summary.get('correct_predictions', 0),
            'total_residues': summary.get('total_residues', 0),
            'accuracy': summary.get('accuracy', 0),
            'avg_confidence': summary.get('avg_confidence', 0),
            'confidence_scores': confidence_scores,
            'original_sequence': original_seq,
            'predicted_sequence': predicted_seq
        }
        fig2 = self.create_accuracy_summary_chart(results_dict, protein_name)
        web_images['accuracy_summary'] = self.fig_to_base64(fig2)
        
        # 3. Confidence Heatmap
        fig3 = self.create_confidence_heatmap(results, protein_name)
        web_images['confidence_heatmap'] = self.fig_to_base64(fig3)
        
        return web_images
