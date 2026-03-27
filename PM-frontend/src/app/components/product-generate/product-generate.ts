// product-generate.component.ts
import { Component, ElementRef, ViewChild, AfterViewChecked, OnDestroy, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { ProductService } from '../../services/product';
import { RouterModule } from '@angular/router';

type AgentStatus = 'idle' | 'running' | 'done' | 'error';

interface AgentState {
  status: AgentStatus;
  progress: number;
  output?: any;
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
  
  // Agent states
  agentStates: { [key: string]: AgentState } = {
    strategist: { status: 'idle', progress: 0, output: null },
    market_research: { status: 'idle', progress: 0, output: null },
    prd: { status: 'idle', progress: 0, output: null },
    tech_architecture: { status: 'idle', progress: 0, output: null },
    ux_design: { status: 'idle', progress: 0, output: null },
    qa_strategy: { status: 'idle', progress: 0, output: null }
  };
  
  // Terminal logs
  logMessages: Array<{ time: string, type: string, text: string }> = [];
  
  // PRD streaming
  prdContent: string = '';
  prdComplete: boolean = false;
  
  // Live output display
  showLiveOutput: boolean = false;
  currentAgentOutput: string = '';
  currentAgentName: string = '';
  private typewriterInterval: any;
  private currentChunkIndex: number = 0;
  private outputChunks: string[] = [];
  private currentProcessingAgent: string = '';
  
  private generateSubscription: Subscription | null = null;
  private logStartTime: number = 0;
  
  @ViewChild('terminalBody') terminalBody!: ElementRef;
  @ViewChild('prdContentEl') prdContentEl!: ElementRef;
  @ViewChild('liveOutputEl') liveOutputEl!: ElementRef;
  
  get currentTime(): string {
    if (!this.logStartTime) return '00:00:00';
    const elapsed = (Date.now() - this.logStartTime) / 1000;
    return elapsed.toFixed(1).padStart(6, '0') + 's';
  }
  
  constructor(
    private productService: ProductService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}
  
  ngAfterViewChecked() {
    if (this.terminalBody) {
      this.terminalBody.nativeElement.scrollTop = this.terminalBody.nativeElement.scrollHeight;
    }
    if (this.prdContentEl && this.prdComplete === false) {
      this.prdContentEl.nativeElement.scrollTop = this.prdContentEl.nativeElement.scrollHeight;
    }
    if (this.liveOutputEl && this.showLiveOutput) {
      this.liveOutputEl.nativeElement.scrollTop = this.liveOutputEl.nativeElement.scrollHeight;
    }
  }
  
  ngOnDestroy(): void {
    this.cancelGeneration();
    if (this.typewriterInterval) {
      clearInterval(this.typewriterInterval);
    }
  }
  
  generateWithStreaming(): void {
    if (!this.idea.trim() || this.isLoading) return;
    
    console.log('🚀 Starting generation for:', this.idea);
    
    this.isLoading = true;
    this.error = null;
    this.prdContent = '';
    this.prdComplete = false;
    this.productId = null;
    this.logMessages = [];
    this.logStartTime = Date.now();
    this.showLiveOutput = false;
    this.currentAgentOutput = '';
    this.currentAgentName = '';
    this.outputChunks = [];
    this.currentChunkIndex = 0;
    this.currentProcessingAgent = '';
    
    // Reset agent states
    Object.keys(this.agentStates).forEach(key => {
      this.agentStates[key] = { status: 'idle', progress: 0, output: null };
    });
    
    this.addLog('info', `Starting generation pipeline for: "${this.idea.substring(0, 60)}..."`);
    
    const request = { idea: this.idea.trim() };
    
    // Call the generate API
    this.generateSubscription = this.productService.generateProduct(request).subscribe({
      next: (response: any) => {
        console.log('📦 API Response received:', response);
        
        if (response.success && response.data) {
          this.productId = response.product_id;
          this.addLog('success', `Product created with ID: ${this.productId}`);
          
          // Check if data has outputs
          console.log('📊 Data keys:', Object.keys(response.data));
          console.log('📊 Strategist:', response.data.strategist ? '✅ Has output' : '❌ No output');
          console.log('📊 Market Research:', response.data.market_research ? '✅ Has output' : '❌ No output');
          console.log('📊 PRD:', response.data.prd ? '✅ Has output' : '❌ No output');
          
          // Start processing agents
          this.processAllAgents(response.data);
          
        } else {
          console.error('❌ Response success false:', response);
          this.addLog('error', response.message || 'Failed to generate product');
          this.error = response.message || 'Failed to generate product';
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('❌ API Error:', err);
        this.addLog('error', 'Failed to generate product. Please check if backend is running.');
        this.error = 'Failed to generate product. Please try again.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }
  
  private processAllAgents(data: any): void {
    const agents = [
      { key: 'strategist', name: 'Strategist', outputKey: 'strategist' },
      { key: 'market_research', name: 'Market Research', outputKey: 'market_research' },
      { key: 'prd', name: 'PRD Writer', outputKey: 'prd' },
      { key: 'tech_architecture', name: 'Tech Architecture', outputKey: 'tech_architecture' },
      { key: 'ux_design', name: 'UX Design', outputKey: 'ux_design' },
      { key: 'qa_strategy', name: 'QA Strategy', outputKey: 'qa_strategy' }
    ];
    
    let currentIndex = 0;
    
    const processNextAgent = () => {
      if (currentIndex >= agents.length) {
        console.log('✅ All agents processed!');
        this.addLog('success', 'All agents completed successfully!');
        this.prdComplete = true;
        this.addLog('success', 'Generation complete!');
        this.isLoading = false;
        this.showLiveOutput = false;
        this.cdr.detectChanges();
        return;
      }
      
      const agent = agents[currentIndex];
      const agentOutput = data[agent.outputKey];
      
      console.log(`🔄 Processing agent ${currentIndex + 1}/${agents.length}: ${agent.key}`, agentOutput ? '✅ Has output' : '❌ No output');
      
      if (agentOutput) {
        // Update UI in Angular zone
        this.ngZone.run(() => {
          // Start agent - show running state
          this.agentStates[agent.key] = { 
            ...this.agentStates[agent.key], 
            status: 'running', 
            progress: 30,
            output: null
          };
          
          // Show live output box
          this.showLiveOutput = true;
          this.currentAgentName = agent.name;
          this.currentAgentOutput = '';
          
          this.addLog('info', `Processing ${agent.name}...`);
          this.cdr.detectChanges();
          
          console.log(`🎬 Agent ${agent.name} started - UI updated`);
        });
        
        // Small delay to show running state
        setTimeout(() => {
          this.ngZone.run(() => {
            // Store output
            this.agentStates[agent.key] = { 
              ...this.agentStates[agent.key], 
              status: 'done', 
              progress: 100,
              output: agentOutput
            };
            
            this.cdr.detectChanges();
            console.log(`✅ Agent ${agent.name} completed - UI updated`);
          });
          
          // Stream the output
          this.streamJSONOutput(agentOutput, agent.name, () => {
            this.ngZone.run(() => {
              this.addLog('success', `${agent.name} complete`);
              currentIndex++;
              this.cdr.detectChanges();
              
              // Process next agent after a delay
              setTimeout(() => {
                processNextAgent();
              }, 500);
            });
          });
        }, 500);
      } else {
        console.warn(`⚠️ No output found for agent: ${agent.key}`);
        currentIndex++;
        processNextAgent();
      }
    };
    
    processNextAgent();
  }
  
  private streamJSONOutput(output: any, agentName: string, onComplete: () => void): void {
    console.log(`📡 Streaming output for ${agentName}...`);
    
    // Format JSON with syntax highlighting
    const formattedJSON = this.formatJSONWithSyntax(output);
    this.outputChunks = this.splitIntoChunks(formattedJSON, 2);
    this.currentChunkIndex = 0;
    
    this.ngZone.run(() => {
      this.currentAgentOutput = '';
      this.currentAgentName = agentName;
      this.showLiveOutput = true;
      this.cdr.detectChanges();
    });
    
    if (this.typewriterInterval) {
      clearInterval(this.typewriterInterval);
    }
    
    // Start typewriter effect
    this.typewriterInterval = setInterval(() => {
      if (this.currentChunkIndex < this.outputChunks.length) {
        this.ngZone.run(() => {
          this.currentAgentOutput += this.outputChunks[this.currentChunkIndex];
          this.currentChunkIndex++;
          this.cdr.detectChanges();
          
          // Auto-scroll live output
          if (this.liveOutputEl) {
            setTimeout(() => {
              this.liveOutputEl.nativeElement.scrollTop = this.liveOutputEl.nativeElement.scrollHeight;
            }, 5);
          }
        });
      } else {
        clearInterval(this.typewriterInterval);
        this.typewriterInterval = null;
        console.log(`✅ Streaming complete for ${agentName}`);
        onComplete();
      }
    }, 15);
  }
  
  private splitIntoChunks(text: string, chunkSize: number): string[] {
    const chunks: string[] = [];
    for (let i = 0; i < text.length; i += chunkSize) {
      chunks.push(text.substring(i, Math.min(i + chunkSize, text.length)));
    }
    return chunks;
  }
  
  private formatJSONWithSyntax(obj: any): string {
    try {
      const jsonString = JSON.stringify(obj, null, 2);
      return this.escapeHtml(jsonString)
        .replace(/&quot;(\w+)&quot;(\s*:)/g, '<span class="json-key">"$1"</span>$2')
        .replace(/: &quot;(.*?)&quot;/g, ': <span class="json-string">"$1"</span>')
        .replace(/: (\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
        .replace(/: (true|false)/g, ': <span class="json-boolean">$1</span>')
        .replace(/: (null)/g, ': <span class="json-null">$1</span>');
    } catch (e) {
      return this.escapeHtml(String(obj));
    }
  }
  
  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
  
  private addLog(type: string, text: string): void {
    const elapsed = this.logStartTime ? ((Date.now() - this.logStartTime) / 1000).toFixed(1) : '0.0';
    this.logMessages.push({
      time: elapsed.padStart(6, '0') + 's',
      type: type,
      text: text
    });
    console.log(`[${type}] ${text}`);
    this.cdr.detectChanges();
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
  
  cancelGeneration(): void {
    if (this.generateSubscription) {
      this.generateSubscription.unsubscribe();
      this.generateSubscription = null;
    }
    if (this.typewriterInterval) {
      clearInterval(this.typewriterInterval);
      this.typewriterInterval = null;
    }
    this.isLoading = false;
    this.addLog('warn', 'Generation cancelled by user');
  }
}