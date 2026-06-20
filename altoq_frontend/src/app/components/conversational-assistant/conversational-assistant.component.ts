import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TemplateService } from '../../services/template.service';
import { ProductService } from '../../services/product.service';
import { AuthService } from '../../services/auth.service';
import { CategoryService } from '../../services/category.service';

@Component({
  selector: 'app-conversational-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './conversational-assistant.component.html',
  styleUrls: ['./conversational-assistant.component.css']
})
export class ConversationalAssistantComponent implements OnInit {
  messages: { sender: string; content: string }[] = [];
  currentQuestion: string = '';
  userInput: string = '';
  productName: string = '';
  productPrice: string = '';
  productDescription: string = '';
  productImage: string = '';
  detectedCategory: any = null;
  collectedData: any = {};
  isTyping: boolean = false;
  isCreatingProduct: boolean = false;
  productCreated: boolean = false;
  categoriesCreated: boolean = false;
  userCategories: string[] = [];

  @Input() storeId: number | null = null;
  @Input() storeName: string = '';
  @Output() productCreatedEvent = new EventEmitter<void>();

  constructor(
    private templateService: TemplateService,
    private productService: ProductService,
    private authService: AuthService,
    private categoryService: CategoryService
  ) {}

  ngOnInit(): void {
    console.log('ConversationalAssistantComponent initialized');
    console.log('StoreId:', this.storeId);
    console.log('StoreName:', this.storeName);
    this.startConversation();
  }

  startConversation(): void {
    this.addMessage('assistant', '¡Hola! Soy tu asistente para crear productos. Primero, necesito que crees las categorías para tu tienda. ¿Qué categorías quieres agregar? (Escribe las categorías separadas por coma, por ejemplo: Ropa, Calzado, Accesorios)');
    this.currentQuestion = 'create_categories';
  }

  addMessage(sender: string, content: string): void {
    this.messages.push({ sender, content });
  }

  handleUserInput(input: string): void {
    if (!input || input.trim() === '') return;
    
    this.addMessage('user', input);
    this.isTyping = true;

    setTimeout(() => {
      this.processInput(input);
      this.isTyping = false;
    }, 500);
  }

  processInput(input: string): void {
    console.log('Processing input:', input, 'Current question:', this.currentQuestion);

    switch (this.currentQuestion) {
      case 'create_categories':
        this.createCategoriesFromInput(input);
        break;
      case 'product_name':
        this.productName = input;
        this.detectCategory(input);
        break;
      case 'product_price':
        this.productPrice = input;
        this.currentQuestion = 'product_description';
        this.addMessage('assistant', 'Perfecto. Ahora, ¿cuál es la descripción de tu producto?');
        break;
      case 'product_description':
        this.productDescription = input;
        this.currentQuestion = 'product_image';
        this.addMessage('assistant', 'Excelente. Por último, ¿cuál es la URL de la imagen de tu producto? (Si no tienes una, escribe "no imagen")');
        break;
      case 'product_image':
        this.productImage = input === 'no imagen' ? '' : input;
        this.completeConversation();
        break;
      case 'confirm_creation':
        if (input.toLowerCase() === 'si' || input.toLowerCase() === 'sí' || input.toLowerCase() === 'yes') {
          this.createProduct();
        } else {
          this.addMessage('assistant', 'Entendido. Si quieres crear el producto más tarde, puedes usar el formulario tradicional.');
          this.resetConversation();
        }
        break;
    }
  }

  createCategoriesFromInput(input: string): void {
    const categories = input.split(',').map(cat => cat.trim()).filter(cat => cat.length > 0);
    
    if (categories.length === 0) {
      this.addMessage('assistant', 'Por favor, ingresa al menos una categoría válida.');
      return;
    }

    this.userCategories = categories;
    this.addMessage('assistant', `Perfecto, voy a crear las siguientes categorías: ${categories.join(', ')}`);
    
    this.createCategoriesInDatabase(categories);
  }

  createCategoriesInDatabase(categories: string[]): void {
    let createdCount = 0;
    let errorCount = 0;
    
    categories.forEach((categoryName, index) => {
      const categoryData = {
        name: categoryName,
        slug: categoryName.toLowerCase().replace(/\s+/g, '-'),
        description: `Categoría para productos de ${categoryName}`
      };

      this.categoryService.createCategory(categoryData).subscribe({
        next: (response) => {
          createdCount++;
          console.log(`Categoría "${categoryName}" creada con ID: ${response.id}`);
          
          if (createdCount + errorCount === categories.length) {
            this.finishCategoryCreation(createdCount, errorCount);
          }
        },
        error: (error) => {
          errorCount++;
          console.error(`Error creando categoría "${categoryName}":`, error);
          
          if (createdCount + errorCount === categories.length) {
            this.finishCategoryCreation(createdCount, errorCount);
          }
        }
      });
    });
  }

  finishCategoryCreation(createdCount: number, errorCount: number): void {
    if (createdCount > 0) {
      this.categoriesCreated = true;
      this.addMessage('assistant', `✅ Categorías creadas exitosamente (${createdCount}). Ahora puedes crear productos.`);
      this.currentQuestion = 'product_name';
      this.addMessage('assistant', '¿Cuál es el nombre del producto que quieres vender?');
    } else {
      this.addMessage('assistant', '❌ Hubo errores al crear las categorías. Por favor, intenta nuevamente.');
    }
  }

  detectCategory(productName: string): void {
    const detectedCategory = this.detectCategoryLocally(productName);
    
    if (detectedCategory) {
      this.detectedCategory = {
        category_id: null,
        template_name: detectedCategory
      };
      this.addMessage('assistant', `He detectado que tu producto pertenece a la categoría: ${detectedCategory}.`);
      this.askForPrice();
    } else {
      this.detectedCategory = {
        category_id: null,
        template_name: 'General'
      };
      this.addMessage('assistant', 'No pude detectar automáticamente la categoría. Se asignará la categoría "General".');
      this.askForPrice();
    }
  }

  detectCategoryLocally(productName: string): string | null {
    const name = productName.toLowerCase();
    
    // Palabras clave para cada categoría
    const categoryKeywords: { [key: string]: string[] } = {
      'Calzado': ['zapato', 'zapatilla', 'bota', 'sandalia', 'tenis', 'chancla', 'calzado', 'pie', 'taco'],
      'Ropa': ['camisa', 'pantalon', 'vestido', 'blusa', 'chaqueta', 'sueter', 'ropa', 'camiseta', 'jeans', 'pantalón'],
      'Electrónica': ['celular', 'telefono', 'laptop', 'computadora', 'tablet', 'auricular', 'cargador', 'electronica', 'tecnologia', 'gadget'],
      'Hogar': ['mesa', 'silla', 'sofa', 'cama', 'lampara', 'cocina', 'hogar', 'mueble', 'decoracion'],
      'Alimentos': ['comida', 'bebida', 'snack', 'dulce', 'postre', 'alimento', 'galleta', 'chocolate'],
      'Deportes': ['balon', 'raqueta', 'bicicleta', 'deporte', 'gimnasio', 'pesa', 'natacion'],
      'Belleza': ['crema', 'maquillaje', 'perfume', 'belleza', 'cabello', 'piel', 'cosmetico'],
      'Juguetes': ['juguete', 'juego', 'muñeco', 'puzzle', 'lego', 'niño', 'infantil'],
      'Libros': ['libro', 'novela', 'comic', 'revista', 'lectura', 'escritura'],
      'Accesorios': ['reloj', 'gafas', 'bolso', 'cartera', 'collar', 'anillo', 'accesorio']
    };

    for (const [category, keywords] of Object.entries(categoryKeywords)) {
      for (const keyword of keywords) {
        if (name.includes(keyword)) {
          return category;
        }
      }
    }

    return null;
  }

  askForPrice(): void {
    this.currentQuestion = 'product_price';
    this.addMessage('assistant', '¿Cuál es el precio de tu producto? (Escribe solo el número, por ejemplo: 50)');
  }

  completeConversation(): void {
    this.addMessage('assistant', '¡Perfecto! He recopilado toda la información necesaria. Tu producto está listo para ser publicado.');
    console.log('Collected data:', this.collectedData);
    
    // Mostrar resumen y botón para crear producto
    const summary = this.generateProductSummary();
    this.addMessage('assistant', `Resumen del producto:\n${summary}\n\n¿Quieres crear este producto ahora? (Responde "si" para confirmar)`);
    this.currentQuestion = 'confirm_creation';
  }

  generateProductSummary(): string {
    let summary = `Nombre: ${this.productName}\n`;
    summary += `Categoría: ${this.detectedCategory.template_name}\n`;
    summary += `Precio: S/. ${this.productPrice}\n`;
    summary += `Descripción: ${this.productDescription}\n`;
    summary += `Imagen: ${this.productImage || 'No especificada'}`;
    return summary;
  }

  createProduct(): void {
    this.isCreatingProduct = true;
    this.addMessage('assistant', 'Creando tu producto...');

    console.log('Creating product with storeId:', this.storeId);
    console.log('Store name:', this.storeName);

    // Construir el objeto del producto
    const productData: any = {
      id: 0, // El backend asignará el ID
      name: this.productName,
      price: parseFloat(this.productPrice) || 0,
      description: this.productDescription,
      image: this.productImage,
      category: '1', // Categoría por defecto (General)
      rating: 0,
      rating_count: 0,
      stock: 10, // Stock por defecto
      specifications: this.collectedData,
      created_at: new Date().toISOString(),
      store_name: this.storeName // Agregar nombre de la tienda
    };

    // Agregar store_id si está disponible
    if (this.storeId) {
      productData.store_id = this.storeId;
      console.log('Adding store_id to product:', this.storeId);
    } else {
      console.warn('storeId is null or undefined');
    }

    console.log('Product data to send:', productData);

    const token = this.authService.getToken();
    const params = token ? { token } : {};

    this.productService.createProduct(productData).subscribe({
      next: (response) => {
        this.isCreatingProduct = false;
        this.productCreated = true;
        this.addMessage('assistant', `✅ ¡Producto "${this.productName}" creado exitosamente para la tienda "${this.storeName}"! Ya está disponible en tu tienda y puedes verlo en "Ver Productos".`);
        console.log('Product created:', response);
        console.log('Product store_id from response:', response.store_id);
        console.log('Emitting productCreatedEvent');
        this.productCreatedEvent.emit();
      },
      error: (error) => {
        this.isCreatingProduct = false;
        console.error('Error creating product:', error);
        this.addMessage('assistant', '❌ Hubo un error al crear el producto. Por favor, intenta nuevamente.');
      }
    });
  }

  resetConversation(): void {
    this.messages = [];
    this.productName = '';
    this.productPrice = '';
    this.productDescription = '';
    this.productImage = '';
    this.detectedCategory = null;
    this.collectedData = {};
    this.currentQuestion = '';
    this.isCreatingProduct = false;
    this.productCreated = false;
    this.categoriesCreated = false;
    this.userCategories = [];
    this.startConversation();
  }
}
