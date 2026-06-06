export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  parent_id?: number;
  created_at: string;
}

export interface CategoryWithProducts extends Category {
  product_count: number;
}

export interface CategoryTree extends Category {
  subcategories: CategoryTree[];
}
