// product-generate.component.ts
import { Component, ElementRef, ViewChild, AfterViewChecked, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { ProductService } from '../../services/product';
import { StreamingService } from '../../services/streaming';
import { StreamEvent } from '../../models/product';
import { RouterModule } from '@angular/router';

type AgentStatus = 'idle' | 'running' | 'done' | 'error';

interface AgentState {
  status: AgentStatus;
  progress: number;
}

@Component({
  selector: 'app-product-generate',
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './product-generate.html',
  styleUrl: './product-generate.scss',
})
export class ProductGenerateComponent implements AfterViewChecked, OnDestroy {
  idea: string = '';
  isLoading: boolean = false;
  error: string | null = null;
  productId: string | null = null;
  
  // Agent states - fixed type to include 'error'
  agentStates: { [key: string]: AgentState } = {
    strategist: { status: 'idle', progress: 0 },
    market_research: { status: 'idle', progress: 0 },
    prd: { status: 'idle', progress: 0 },
    tech_architecture: { status: 'idle', progress: 0 },
    ux_design: { status: 'idle', progress: 0 },
    qa_strategy: { status: 'idle', progress: 0 }
  };
  
  // Terminal logs
  logMessages: Array<{ time: string, type: string, text: string }> = [];
  
  // PRD streaming
  prdContent: string = '';
  prdComplete: boolean = false;
  
  private streamSubscription: Subscription | null = null;
  private logStartTime: number = 0;
  
  @ViewChild('terminalBody') terminalBody!: ElementRef;
  @ViewChild('prdContentEl') prdContentEl!: ElementRef;
  
  get currentTime(): string {
    if (!this.logStartTime) return '00:00:00';
    const elapsed = (Date.now() - this.logStartTime) / 1000;
    return elapsed.toFixed(1).padStart(6, '0') + 's';
  }
  
  constructor(
    private productService: ProductService,
    private streamingService: StreamingService
  ) {}
  
  ngAfterViewChecked() {
    // Auto-scroll terminal
    if (this.terminalBody) {
      this.terminalBody.nativeElement.scrollTop = this.terminalBody.nativeElement.scrollHeight;
    }
    // Auto-scroll PRD content
    if (this.prdContentEl && this.prdComplete === false) {
      this.prdContentEl.nativeElement.scrollTop = this.prdContentEl.nativeElement.scrollHeight;
    }
  }
  
  ngOnDestroy(): void {
    this.cancelStream();
  }
  
  generateWithStreaming(): void {
    if (!this.idea.trim() || this.isLoading) return;
    
    this.isLoading = true;
    this.error = null;
    this.prdContent = '';
    this.prdComplete = false;
    this.productId = null;
    this.logMessages = [];
    this.logStartTime = Date.now();
    
    // Reset agent states
    Object.keys(this.agentStates).forEach(key => {
      this.agentStates[key] = { status: 'idle', progress: 0 };
    });
    
    this.addLog('info', `Starting generation pipeline for: "${this.idea.substring(0, 60)}..."`);
    
    this.streamSubscription = this.streamingService.connectStream(this.idea.trim())
      .subscribe({
        next: (event: StreamEvent) => this.handleSSEEvent(event),
        error: (err) => {
          console.error('Streaming error:', err);
          this.addLog('error', 'Connection error. Please try again.');
          this.error = 'Connection error. Please try again.';
          this.isLoading = false;
        },
        complete: () => {
          this.isLoading = false;
        }
      });
  }
  
  private handleSSEEvent(event: StreamEvent): void {
    switch (event.type) {
      case 'start':
        this.addLog('info', event.message || 'Pipeline started');
        break;
        
      case 'product_created':
        this.addLog('success', event.message || `Product created: ${event.product_id}`);
        this.productId = event.product_id || null;
        break;
        
      case 'agent_start':
        const agentKey = (event.agent || '').replace('_node', '');
        if (this.agentStates[agentKey]) {
          this.agentStates[agentKey].status = 'running';
          this.agentStates[agentKey].progress = 30;
        }
        this.addLog('info', event.message || `Starting ${agentKey}...`);
        break;
        
      case 'agent_complete':
        const doneKey = (event.agent || '').replace('_node', '');
        if (this.agentStates[doneKey]) {
          this.agentStates[doneKey].status = 'done';
          this.agentStates[doneKey].progress = 100;
        }
        this.addLog('success', event.message || `${doneKey} complete`);
        break;
        
      case 'generating_final':
        this.addLog('info', event.message || 'Generating final PRD...');
        break;
        
      case 'prd_chunk':
        if (event.chunk) {
          this.prdContent += event.chunk;
        }
        break;
        
      case 'prd_complete':
        this.prdComplete = true;
        this.addLog('success', event.message || 'PRD complete');
        break;
        
      case 'complete':
        this.addLog('success', event.message || 'Generation complete!');
        if (event.product_id) this.productId = event.product_id;
        this.isLoading = false;
        break;
        
      case 'error':
        this.addLog('error', event.error || 'Unknown error');
        this.error = event.error || 'An error occurred';
        this.isLoading = false;
        break;
        
      case 'end':
        this.addLog('info', event.message || 'Stream ended');
        break;
        
      default:
        // Handle any other event types
        console.log('Unknown event type:', event.type);
        break;
    }
  }
  
  private addLog(type: string, text: string): void {
    const elapsed = this.logStartTime ? ((Date.now() - this.logStartTime) / 1000).toFixed(1) : '0.0';
    this.logMessages.push({
      time: elapsed.padStart(6, '0') + 's',
      type: type,
      text: text
    });
  }
  
  isAgentRunning(agent: string): boolean {
    return this.agentStates[agent]?.status === 'running';
  }
  
  isAgentDone(agent: string): boolean {
    return this.agentStates[agent]?.status === 'done';
  }
  
  hasAgentError(agent: string): boolean {
    return this.agentStates[agent]?.status === 'error';
  }
  
  getAgentStatus(agent: string): string {
    const state = this.agentStates[agent];
    if (!state) return '○ Waiting';
    switch (state.status) {
      case 'running': return '● Running...';
      case 'done': return '✓ Complete';
      case 'error': return '✗ Error';
      default: return '○ Waiting';
    }
  }
  
  getAgentProgress(agent: string): number {
    return this.agentStates[agent]?.progress || 0;
  }
  
  cancelStream(): void {
    if (this.streamSubscription) {
      this.streamSubscription.unsubscribe();
      this.streamSubscription = null;
    }
    this.isLoading = false;
    this.addLog('warn', 'Generation cancelled by user');
  }
}