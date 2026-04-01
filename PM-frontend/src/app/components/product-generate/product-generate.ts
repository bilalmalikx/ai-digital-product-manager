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

interface UploadedFile {
  name: string;
  size: number;
  type: string;
  file: File;
  status: 'pending' | 'uploading' | 'done' | 'error';
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
  
  // Multi-format inputs
  uploadedFiles: UploadedFile[] = [];
  urls: string = '';
  showAdvanced: boolean = false;
  
  // Drag and drop
  isDragging: boolean = false;
  
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
  
  private generateSubscription: Subscription | null = null;
  private logStartTime: number = 0;
  
  @ViewChild('terminalBody') terminalBody!: ElementRef;
  @ViewChild('prdContentEl') prdContentEl!: ElementRef;
  @ViewChild('liveOutputEl') liveOutputEl!: ElementRef;
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  @ViewChild('dropZone') dropZone!: ElementRef;
  
  get currentTime(): string {
    if (!this.logStartTime) return '00:00:00';
    const elapsed = (Date.now() - this.logStartTime) / 1000;
    return elapsed.toFixed(1).padStart(6, '0') + 's';
  }
  
  get totalFileSize(): string {
    const total = this.uploadedFiles.reduce((sum, f) => sum + f.size, 0);
    if (total < 1024 * 1024) return `${(total / 1024).toFixed(1)} KB`;
    return `${(total / (1024 * 1024)).toFixed(1)} MB`;
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
    if (this.prdContentEl && !this.prdComplete) {
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
  
  // ==================== FILE HANDLING ====================
  
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.addFiles(Array.from(input.files));
    }
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }
  
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }
  
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }
  
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
    
    const files = event.dataTransfer?.files;
    if (files) {
      this.addFiles(Array.from(files));
    }
  }
  
  private addFiles(files: File[]): void {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/plain',
      'text/markdown',
      'audio/mpeg',
      'audio/wav',
      'video/mp4'
    ];
    
    for (const file of files) {
      if (validTypes.includes(file.type) || file.name.endsWith('.md') || file.name.endsWith('.txt')) {
        this.uploadedFiles.push({
          name: file.name,
          size: file.size,
          type: file.type,
          file: file,
          status: 'pending'
        });
        this.addLog('info', `📎 Added file: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`);
      } else {
        this.addLog('warn', `⚠️ Skipped unsupported file: ${file.name}`);
      }
    }
    this.cdr.detectChanges();
  }
  
  removeFile(index: number): void {
    const removed = this.uploadedFiles.splice(index, 1)[0];
    this.addLog('info', `🗑️ Removed file: ${removed.name}`);
    this.cdr.detectChanges();
  }
  
  clearAllFiles(): void {
    this.uploadedFiles = [];
    this.addLog('info', '🗑️ Cleared all files');
    this.cdr.detectChanges();
  }
  
  // ==================== GENERATION ====================
  
  generateWithStreaming(): void {
    if ((!this.idea.trim() && this.uploadedFiles.length === 0 && !this.urls.trim()) || this.isLoading) {
      this.addLog('warn', '⚠️ Please enter an idea, upload files, or add URLs');
      return;
    }
    
    console.log('🚀 Starting generation with:', {
      idea: this.idea,
      files: this.uploadedFiles.length,
      urls: this.urls
    });
    
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
    
    // Reset agent states
    Object.keys(this.agentStates).forEach(key => {
      this.agentStates[key] = { status: 'idle', progress: 0, output: null };
    });
    
    this.addLog('info', `🚀 Starting generation pipeline...`);
    
    if (this.idea.trim()) {
      this.addLog('info', `📝 Idea: "${this.idea.substring(0, 80)}..."`);
    }
    if (this.uploadedFiles.length > 0) {
      this.addLog('info', `📎 Files: ${this.uploadedFiles.length} file(s) (${this.totalFileSize})`);
    }
    if (this.urls.trim()) {
      const urlList = this.urls.split(',').map(u => u.trim()).filter(u => u);
      this.addLog('info', `🔗 URLs: ${urlList.length} URL(s)`);
    }
    
    // Prepare form data for multi-format upload
    const formData = new FormData();
    
    if (this.idea.trim()) {
      formData.append('idea', this.idea.trim());
    }
    
    for (const fileItem of this.uploadedFiles) {
      formData.append('files', fileItem.file);
    }
    
    if (this.urls.trim()) {
      formData.append('urls', this.urls);
    }
    
    // Use the multi-format endpoint
    this.generateSubscription = this.productService.generateProductFromFiles(formData).subscribe({
      next: (response: any) => {
        console.log('📦 API Response received:', response);
        
        if (response.success && response.outputs) {
          this.productId = response.product_id;
          this.addLog('success', `✅ Product created with ID: ${this.productId}`);
          this.addLog('info', `📊 Processed ${response.input_summary?.sources_processed || 0} source(s)`);
          this.addLog('info', `💡 Consolidated idea: "${response.input_summary?.consolidated_idea?.substring(0, 80)}..."`);
          
          // Process all agents
          this.processAllAgents(response.outputs);
          
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
        this.addLog('success', '✨ All agents completed successfully!');
        this.prdComplete = true;
        this.addLog('success', '🎉 Generation complete! Your product documentation is ready.');
        this.isLoading = false;
        this.showLiveOutput = false;
        this.cdr.detectChanges();
        return;
      }
      
      const agent = agents[currentIndex];
      const agentOutput = data[agent.outputKey];
      
      console.log(`🔄 Processing agent ${currentIndex + 1}/${agents.length}: ${agent.key}`, agentOutput ? '✅ Has output' : '❌ No output');
      
      if (agentOutput) {
        this.ngZone.run(() => {
          this.agentStates[agent.key] = { 
            ...this.agentStates[agent.key], 
            status: 'running', 
            progress: 30,
            output: null
          };
          
          this.showLiveOutput = true;
          this.currentAgentName = agent.name;
          this.currentAgentOutput = '';
          
          this.addLog('info', `🤖 Processing ${agent.name}...`);
          this.cdr.detectChanges();
        });
        
        setTimeout(() => {
          this.ngZone.run(() => {
            this.agentStates[agent.key] = { 
              ...this.agentStates[agent.key], 
              status: 'done', 
              progress: 100,
              output: agentOutput
            };
            
            // Check if this is the final PRD output
            if (agent.key === 'prd' && agentOutput.final_prd) {
              this.streamPRDContent(agentOutput.final_prd);
            }
            
            this.cdr.detectChanges();
          });
          
          this.streamJSONOutput(agentOutput, agent.name, () => {
            this.ngZone.run(() => {
              this.addLog('success', `✓ ${agent.name} complete`);
              currentIndex++;
              this.cdr.detectChanges();
              
              setTimeout(() => {
                processNextAgent();
              }, 300);
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
    const formattedJSON = this.formatJSONWithSyntax(output);
    this.outputChunks = this.splitIntoChunks(formattedJSON, 3);
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
    
    this.typewriterInterval = setInterval(() => {
      if (this.currentChunkIndex < this.outputChunks.length) {
        this.ngZone.run(() => {
          this.currentAgentOutput += this.outputChunks[this.currentChunkIndex];
          this.currentChunkIndex++;
          this.cdr.detectChanges();
          
          if (this.liveOutputEl) {
            setTimeout(() => {
              this.liveOutputEl.nativeElement.scrollTop = this.liveOutputEl.nativeElement.scrollHeight;
            }, 5);
          }
        });
      } else {
        clearInterval(this.typewriterInterval);
        this.typewriterInterval = null;
        onComplete();
      }
    }, 12);
  }
  
  private streamPRDContent(content: string): void {
    this.ngZone.run(() => {
      this.prdContent = '';
      this.prdComplete = false;
      this.cdr.detectChanges();
    });
    
    const chunks = this.splitIntoChunks(content, 2);
    let index = 0;
    
    const streamInterval = setInterval(() => {
      if (index < chunks.length) {
        this.ngZone.run(() => {
          this.prdContent += chunks[index];
          index++;
          this.cdr.detectChanges();
          
          if (this.prdContentEl) {
            setTimeout(() => {
              this.prdContentEl.nativeElement.scrollTop = this.prdContentEl.nativeElement.scrollHeight;
            }, 5);
          }
        });
      } else {
        clearInterval(streamInterval);
        this.ngZone.run(() => {
          this.prdComplete = true;
          this.cdr.detectChanges();
        });
      }
    }, 10);
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
    this.addLog('warn', '⏹️ Generation cancelled by user');
  }
}