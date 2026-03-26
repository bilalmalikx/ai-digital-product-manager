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
}

export interface ProductGenerateRequest {
  idea: string;
  product_id?: string;
}

export interface ProductResponse {
  success: boolean;
  data?: Product;
  message?: string;
  error?: string;
  product_id?: string;
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
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  skip: number;
  limit: number;
}