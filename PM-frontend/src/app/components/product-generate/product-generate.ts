import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { StreamEvent } from '../../models/product';
import { Subscription } from 'rxjs';
import { ProductService } from '../../services/product';
import { StreamingService } from '../../services/streaming';


@Component({
  selector: 'app-product-generate',
  standalone: true,
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './product-generate.component.html',
  styleUrls: ['./product-generate.component.scss']
})
export class ProductGenerateComponent implements OnInit, OnDestroy {
  idea: string = '';
  isLoading: boolean = false;
  streamMessages: StreamEvent[] = [];
  productId: string | null = null;
  error: string | null = null;
  private streamSubscription: Subscription | null = null;

  constructor(
    private productService: ProductService,
    private streamingService: StreamingService
  ) {}

  ngOnInit(): void {}

  generateWithStreaming(): void {
    if (!this.idea.trim()) return;

    this.isLoading = true;
    this.streamMessages = [];
    this.productId = null;
    this.error = null;

    this.streamSubscription = this.streamingService.connectStream(this.idea.trim())
      .subscribe({
        next: (event: StreamEvent) => {
          this.streamMessages.push(event);
          
          if (event.type === 'complete' && event.product_id) {
            this.productId = event.product_id;
            this.isLoading = false;
          }
          
          if (event.type === 'error') {
            this.error = event.error || 'An error occurred';
            this.isLoading = false;
          }
          
          if (event.type === 'end') {
            this.isLoading = false;
          }
        },
        error: (err) => {
          console.error('Streaming error:', err);
          this.error = 'Connection error. Please try again.';
          this.isLoading = false;
        }
      });
  }

  cancelStream(): void {
    if (this.streamSubscription) {
      this.streamSubscription.unsubscribe();
      this.streamSubscription = null;
    }
    this.isLoading = false;
  }

  getMessageIcon(type: string): string {
    switch(type) {
      case 'start': return '🚀';
      case 'agent_complete': return '✅';
      case 'generating_final': return '📝';
      case 'complete': return '🎉';
      case 'error': return '❌';
      case 'end': return '🏁';
      default: return '📌';
    }
  }

  getAgentName(agent: string): string {
    const names: {[key: string]: string} = {
      'strategist_node': 'Strategist',
      'market_research_node': 'Market Research',
      'prd_node': 'PRD Generation',
      'tech_architecture_node': 'Tech Architecture',
      'ux_design_node': 'UX Design',
      'qa_strategy_node': 'QA Strategy'
    };
    return names[agent] || agent.replace('_', ' ').toUpperCase();
  }

  ngOnDestroy(): void {
    this.cancelStream();
  }
}