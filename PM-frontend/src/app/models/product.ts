export interface Product {
  id: string;
  name: string;
  description?: string;
  idea: string;
  status: 'draft' | 'in_review' | 'approved' | 'rejected';
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
  data?: any;
  message?: string;
  error?: string;
  product_id?: string;
}

export interface StreamEvent {
  type: 'start' | 'agent_complete' | 'generating_final' | 'complete' | 'error' | 'end';
  agent?: string;
  output?: any;
  message?: string;
  error?: string;
  product_id?: string;
  outputs?: any;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  skip: number;
  limit: number;
}