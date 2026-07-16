import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart';
import { FavoritesService } from '../../services/favorites.service';
import { ToastService } from '../../services/toast.service';
import { ProductCard } from '../../components/product-card/product-card';
import { ReviewService, Review } from '../../services/review.service';
import { StoreService } from '../../services/store.service';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ProductCard],
  templateUrl: './product-detail.html',
  styleUrl: './product-detail.css',
})
export class ProductDetailComponent implements OnInit {
  Object = Object; // Expose Object constructor to template
  product?: Product;
  loading = true;
  error?: string;
  selectedImage: string | null = null;
  selectedColor: string | null = null;
  quantity: number = 1;
  showAllSpecs: boolean = false;
  isFavorite: boolean = false;
  relatedProducts: Product[] = [];
  sizes: string[] = [];
  selectedSize: string | null = null;
  reviews: Review[] = [];
  
  // Pending review & Banner logic
  canReview = false;
  pendingOrderId: number | null = null;
  showReviewBanner = false;
  storeDetails: any = null;

  // Direct review modal/form state
  showReviewModal = false;
  reviewRating = 5;
  reviewStoreRating = 5;
  reviewComment = '';
  reviewImageFile: File | null = null;
  reviewImagePreview: string | null = null;
  isSubmittingReview = false;

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private cartService: CartService,
    private favoritesService: FavoritesService,
    private toastService: ToastService,
    private reviewService: ReviewService,
    private storeService: StoreService
  ) {}


  ngOnInit(): void {
    // Subscribe to paramMap so the page reloads when navigating between products
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      const id = idParam ? Number(idParam) : NaN;

      if (!id) {
        this.error = 'Producto no encontrado';
        this.loading = false;
        return;
      }

      // Reset state for new product
      this.loading = true;
      this.error = undefined;
      this.product = undefined;
      this.selectedImage = null;
      this.selectedColor = null;
      this.quantity = 1;
      this.relatedProducts = [];
      this.sizes = [];
      this.selectedSize = null;

      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });

      this.loadProduct(id);
    });
  }

  private loadProduct(id: number): void {
    this.productService.getProductById(id).subscribe({
      next: (product) => {
        this.product = product;
        if (product) {
          this.selectedImage = product.image;
          this.isFavorite = this.favoritesService.isFavorite(product.id);
          
          // Mock colors and images for testing
          const catName = (product.category || '').toLowerCase() + (product.name || '').toLowerCase();
          if (product.id === 1) {
             this.product.images = [
               product.image,
               'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=60'
             ];
             this.product.colors = ['Negro', 'Plata', 'Azul'];
             this.product.sales = 25;
          } else {
             if (catName.includes('calzado') || catName.includes('zapato') || catName.includes('zapatilla') || catName.includes('tacon') || catName.includes('pantufla')) {
               this.product.colors = ['Camel', 'Rosa', 'Gris', 'Negro'];
               if (!product.images || product.images.length <= 1) {
                 this.product.images = [
                   product.image,
                   product.image,
                   product.image,
                   product.image,
                   product.image
                 ];
               }
             } else {
               this.product.colors = ['Estándar'];
             }
             this.product.sales = 15;
          }

          // Ensure store_id and store_name are set
          if (!this.product.store_id) {
            this.product.store_id = 1;
          }
          if (!this.product.store_name) {
            if (catName.includes('calzado') || catName.includes('zapato') || catName.includes('zapatilla') || catName.includes('tacon') || catName.includes('pantufla')) {
              this.product.store_name = 'Tienda de Calzado';
            } else {
              this.product.store_name = 'Tienda Oficial';
            }
          } else {
            this.product.store_name = this.toTitleCase(this.product.store_name);
          }
          
          if (this.product.colors && this.product.colors.length > 0) {
            this.selectedColor = this.product.colors[0];
          }

          // Populate sizes based on product category/name
          if (catName.includes('calzado') || catName.includes('zapato') || catName.includes('zapatilla') || catName.includes('tacon') || catName.includes('pantufla')) {
            this.sizes = ['36', '37', '38', '39', '40', '41'];
            this.selectedSize = '38';
          } else if (catName.includes('ropa') || catName.includes('polo') || catName.includes('camisa') || catName.includes('pantalon') || catName.includes('vestido')) {
            this.sizes = ['S', 'M', 'L', 'XL'];
            this.selectedSize = 'M';
          } else {
            this.sizes = [];
            this.selectedSize = null;
          }

              // Fetch related products — ONLY same category
              const productCategory = (product.category || '').toLowerCase();
              this.productService.getProducts().subscribe({
                next: (products) => {
                  this.relatedProducts = products
                    .filter(p => p.id !== id && (p.category || '').toLowerCase() === productCategory)
                    .slice(0, 4);
                }
              });

              // Fetch reviews
              this.loadReviews(product.id);

              // Check if user can review
              this.checkIfUserCanReview(product.id);

              // Fetch store details
              if (product.store_id) {
                this.loadStoreDetails(product.store_id);
              }
            }
            this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el producto';
        this.loading = false;
      },
    });
  }

  getColorClass(color: string): string {
    const c = color.toLowerCase();
    if (c.includes('camel')) return '#c29864';
    if (c.includes('rosa') || c.includes('pink') || c.includes('rosado')) return '#f0b2c7';
    if (c.includes('gris') || c.includes('grey') || c.includes('plata')) return '#9ca3af';
    if (c.includes('negro') || c.includes('black')) return '#1e293b';
    if (c.includes('azul') || c.includes('blue')) return '#1d4ed8';
    return '#cbd5e1'; // fallback slate-300
  }

  toggleFavorite(): void {
    if (!this.product) return;
    const added = this.favoritesService.toggle(this.product);
    this.isFavorite = added;
    if (added) {
      this.toastService.show('Producto agregado a favoritos', 'success');
    } else {
      this.toastService.show('Producto eliminado de favoritos', 'info');
    }
  }

  selectImage(image: string) {
    this.selectedImage = image;
  }
  
  selectColor(color: string) {
    this.selectedColor = color;
  }

  incrementQuantity() {
    if (this.product && this.quantity < this.product.stock) {
      this.quantity++;
    }
  }

  decrementQuantity() {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  get galleryImages(): string[] {
    if (!this.product) return [];
    if (this.product.images && this.product.images.length > 0) {
      return this.product.images;
    }
    // Fallback: use main image if no gallery exists
    return this.product.image ? [this.product.image] : []; 
  }

  prevImage() {
    const imgs = this.galleryImages;
    if (imgs.length <= 1 || !this.selectedImage) return;
    const idx = imgs.indexOf(this.selectedImage);
    if (idx > 0) {
      this.selectedImage = imgs[idx - 1];
    } else {
      this.selectedImage = imgs[imgs.length - 1];
    }
  }

  nextImage() {
    const imgs = this.galleryImages;
    if (imgs.length <= 1 || !this.selectedImage) return;
    const idx = imgs.indexOf(this.selectedImage);
    if (idx < imgs.length - 1) {
      this.selectedImage = imgs[idx + 1];
    } else {
      this.selectedImage = imgs[0];
    }
  }

  getStarsFor(product: Product): number[] {
    const stars = [];
    let rating = product.rating || 0;
    for (let i = 0; i < 5; i++) {
        if (rating >= 1) {
            stars.push(1);
            rating--;
        } else if (rating >= 0.5) {
            stars.push(0.5);
            rating = 0;
        } else {
            stars.push(0);
        }
    }
    return stars;
  }

  addToCart(): void {
    if (!this.product) return;

    this.cartService.addToCart({
      productId: this.product.id,
      quantity: this.quantity,
      price: this.product.price,
      name: this.product.name,
      image: this.product.image,
      storeId: this.product.store_id,
      stock: this.product.stock
    });
    
    // Optional: Feedback to user about color
    // (CartService already shows a toast message for the basic item)
  }

  getStars(): number[] {
    if (!this.product) return [];
    const stars = [];
    let rating = this.product.rating || 0;
    for (let i = 0; i < 5; i++) {
        if (rating >= 1) {
            stars.push(1);
            rating--;
        } else if (rating >= 0.5) {
            stars.push(0.5);
            rating = 0;
        } else {
            stars.push(0);
        }
    }
    return stars;
  }

  toggleSpecs(): void {
    this.showAllSpecs = !this.showAllSpecs;
  }

  get visibleSpecs(): [string, string][] {
    if (!this.product?.specifications) return [];
    
    const entries = Object.entries(this.product.specifications);
    if (this.showAllSpecs || entries.length <= 4) {
      return entries;
    }
    return entries.slice(0, 4);
  }

  get hasMoreSpecs(): boolean {
    if (!this.product?.specifications) return false;
    return Object.keys(this.product.specifications).length > 4;
  }

  keyContains(key: string, term: string): boolean {
    return key.toLowerCase().includes(term.toLowerCase());
  }

  isCustomSpec(key: string): boolean {
    const k = key.toLowerCase();
    return k.includes('material') || k.includes('lana') || k.includes('algodón') ||
           k.includes('suela') || k.includes('antideslizante') || k.includes('seguridad') ||
           k.includes('livian') || k.includes('comod') || k.includes('peso') || k.includes('diario') ||
           k.includes('limpiar') || k.includes('lavar') || k.includes('resistente') || k.includes('limpio');
  }

  toTitleCase(str: string): string {
    if (!str) return '';
    return str.toLowerCase().split(' ').map(word => {
      return word.charAt(0).toUpperCase() + word.slice(1);
    }).join(' ');
  }

  private loadReviews(productId: number): void {
    this.reviewService.getProductReviews(productId).subscribe({
      next: (reviews) => {
        this.reviews = reviews;
      },
      error: (err) => {
        console.error('Error loading product reviews:', err);
      }
    });
  }

  getStarsForRating(rating: number): number[] {
    const stars = [];
    let r = rating;
    for (let i = 0; i < 5; i++) {
        if (r >= 1) {
            stars.push(1);
            r--;
        } else if (r >= 0.5) {
            stars.push(0.5);
            r = 0;
        } else {
            stars.push(0);
        }
    }
    return stars;
  }

  checkIfUserCanReview(productId: number): void {
    this.reviewService.checkPendingReview(productId).subscribe({
      next: (res) => {
        this.canReview = res.can_review;
        this.pendingOrderId = res.order_id;
        this.showReviewBanner = res.can_review;
      },
      error: (err) => {
        console.error('Error checking pending review:', err);
      }
    });
  }

  loadStoreDetails(storeId: number): void {
    this.storeService.getPublicStore(storeId).subscribe({
      next: (store) => {
        this.storeDetails = store;
      },
      error: (err) => {
        console.error('Error loading store details for product:', err);
      }
    });
  }

  openReviewModal(): void {
    this.reviewRating = 5;
    this.reviewStoreRating = 5;
    this.reviewComment = '';
    this.reviewImageFile = null;
    this.reviewImagePreview = null;
    this.showReviewModal = true;
  }

  closeReviewModal(): void {
    this.showReviewModal = false;
  }

  setReviewRating(rating: number): void {
    this.reviewRating = rating;
  }

  setReviewStoreRating(rating: number): void {
    this.reviewStoreRating = rating;
  }

  onReviewImageSelected(event: any): void {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        this.toastService.show('Por favor selecciona una imagen válida', 'error');
        return;
      }
      this.reviewImageFile = file;
      const reader = new FileReader();
      reader.onload = () => {
        this.reviewImagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  submitReview(): void {
    if (!this.product || !this.pendingOrderId) return;
    this.isSubmittingReview = true;

    const saveReview = (imageUrl?: string) => {
      const reviewData = {
        product_id: this.product!.id,
        order_id: this.pendingOrderId!,
        rating: this.reviewRating,
        store_rating: this.reviewStoreRating,
        comment: this.reviewComment || undefined,
        image_url: imageUrl || undefined
      };

      this.reviewService.createReview(reviewData).subscribe({
        next: (review) => {
          this.toastService.show('¡Reseña publicada exitosamente!', 'success');
          
          this.reviews.unshift(review);
          
          // Re-calculate product ratings locally
          const totalRating = this.reviews.reduce((sum, r) => sum + r.rating, 0);
          this.product!.rating = Number((totalRating / this.reviews.length).toFixed(1));
          this.product!.rating_count = this.reviews.length;
          
          this.canReview = false;
          this.showReviewBanner = false;
          this.isSubmittingReview = false;
          
          // Reload store details to reflect new ratings/reviews
          if (this.product!.store_id) {
            this.loadStoreDetails(this.product!.store_id);
          }

          this.closeReviewModal();
        },
        error: (err) => {
          console.error('Error submitting review:', err);
          this.toastService.show('Error al publicar la reseña: ' + (err.error?.detail || err.message), 'error');
          this.isSubmittingReview = false;
        }
      });
    };

    if (this.reviewImageFile) {
      this.reviewService.uploadReviewImage(this.reviewImageFile).subscribe({
        next: (res) => {
          saveReview(res.image_url);
        },
        error: (err) => {
          console.error('Error uploading review image:', err);
          this.toastService.show('Error al subir la imagen, guardando reseña sin foto...', 'info');
          saveReview();
        }
      });
    } else {
      saveReview();
    }
  }

  closeBanner(): void {
    this.showReviewBanner = false;
  }
}
