// product.model.ts

export interface Product {
  id: string;
  name: string;
  description?: string;
  idea: string;
  status: 'draft' | 'in_review' | 'approved' | 'rejected' | 'pending' | 'completed' | 'generating';
  strategist_output?: any;
  market_research_output?: any;
  prd_output?: any;
  tech_architecture?: any;
  ux_design?: any;
  qa_strategy?: any;
  final_prd?: string;
  created_at: Date;
  updated_at: Date;
  
  // NEW: Multi-format input support
  input_sources?: InputSource[];
  consolidated_idea?: string;
  extracted_requirements?: string[];
  constraints?: string[];
  stakeholders?: string[];
  generation_time?: number;
}

// NEW: Input source interface
export interface InputSource {
  type: 'text' | 'file' | 'url' | 'audio' | 'video';
  name: string;
  content_preview?: string;
  size?: number;
  url?: string;
  processed_at?: Date;
  error?: string;
}

export interface ProductGenerateRequest {
  idea: string;
  product_id?: string;
  files?: File[];      // NEW: For multi-format file upload
  urls?: string[];     // NEW: For URL inputs
}

export interface ProductResponse {
  success: boolean;
  data?: Product;
  message?: string;
  error?: string;
  product_id?: string;
  
  // NEW: For multi-format response
  input_summary?: InputSummary;
  outputs?: any;
}

// NEW: Input summary interface
export interface InputSummary {
  sources_processed: number;
  consolidated_idea: string;
  requirements_found: number;
  constraints_found: number;
  files_processed: string[];
  urls_processed: string[];
}

export interface StreamEvent {
  type: 'start' | 'agent_start' | 'agent_complete' | 'product_created' | 'outputs_update' | 'generating_final' | 'prd_chunk' | 'prd_complete' | 'complete' | 'error' | 'end';
  agent?: string;
  output?: any;
  message?: string;
  error?: string;
  product_id?: string;
  outputs?: any;
  chunk?: string;
  
  // NEW: Progress tracking
  progress?: number;
  timestamp?: Date;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  skip: number;
  limit: number;
}