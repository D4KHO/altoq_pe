import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TemplateService } from '../../services/template.service';
import { ProductService } from '../../services/product.service';
import { AuthService } from '../../services/auth.service';

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
  detectedCategory: any = null;
  templateFields: any[] = [];
  currentFieldIndex: number = 0;
  collectedData: any = {};
  isTyping: boolean = false;
  isCreatingProduct: boolean = false;
  productCreated: boolean = false;

  constructor(
    private templateService: TemplateService,
    private productService: ProductService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.startConversation();
  }

  startConversation(): void {
    this.addMessage('assistant', '¡Hola! Soy tu asistente para crear productos. ¿Cuál es el nombre del producto que quieres vender?');
    this.currentQuestion = 'product_name';
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
      case 'product_name':
        this.productName = input;
        this.detectCategory(input);
        break;
      case 'collect_fields':
        this.collectFieldData(input);
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

  detectCategory(productName: string): void {
    this.templateService.detectCategory(productName).subscribe({
      next: (response) => {
        if (response.category_id) {
          this.detectedCategory = response;
          this.templateFields = response.fields || [];
          this.addMessage('assistant', `He detectado que tu producto es de la categoría: ${response.template_name}. Ahora necesito que me des algunos detalles específicos.`);
          this.currentQuestion = 'collect_fields';
          this.askNextField();
        } else {
          this.addMessage('assistant', 'No pude detectar automáticamente la categoría. Por favor, selecciona una categoría manualmente.');
        }
      },
      error: (error) => {
        console.error('Error detecting category:', error);
        this.addMessage('assistant', 'Hubo un error al detectar la categoría. Por favor, intenta nuevamente.');
      }
    });
  }

  askNextField(): void {
    if (this.currentFieldIndex < this.templateFields.length) {
      const field = this.templateFields[this.currentFieldIndex];
      this.addMessage('assistant', `${field.label}${field.required ? ' (requerido)' : ''}`);
    } else {
      this.completeConversation();
    }
  }

  collectFieldData(input: string): void {
    if (this.currentFieldIndex < this.templateFields.length) {
      const field = this.templateFields[this.currentFieldIndex];
      this.collectedData[field.name] = input;
      this.currentFieldIndex++;
      this.askNextField();
    }
  }

  completeConversation(): void {
    this.addMessage('assistant', '¡Perfecto! He recopilado toda la información necesaria. Tu producto está listo para ser publicado.');
    console.log('Collected data:', this.collectedData);
    
    // Mostrar resumen y botón para crear producto
    const summary = this.generateProductSummary();
    this.addMessage('assistant', `Resumen del producto:\n${summary}\n\n¿Quieres crear este producto ahora?`);
    this.currentQuestion = 'confirm_creation';
  }

  generateProductSummary(): string {
    let summary = `Nombre: ${this.productName}\n`;
    summary += `Categoría: ${this.detectedCategory.template_name}\n`;
    for (const [key, value] of Object.entries(this.collectedData)) {
      summary += `${key}: ${value}\n`;
    }
    return summary;
  }

  createProduct(): void {
    this.isCreatingProduct = true;
    this.addMessage('assistant', 'Creando tu producto...');
    
    // Construir el objeto del producto
    const productData = {
      id: 0, // El backend asignará el ID
      name: this.productName,
      price: 0, // Precio por defecto, el usuario puede actualizarlo después
      description: `Producto creado con asistente conversacional. Categoría: ${this.detectedCategory.template_name}`,
      image: '',
      category: this.detectedCategory.category_id.toString(),
      rating: 0,
      rating_count: 0,
      stock: 10, // Stock por defecto
      specifications: this.collectedData,
      created_at: new Date().toISOString()
    };

    const token = this.authService.getToken();
    const params = token ? { token } : {};

    this.productService.createProduct(productData).subscribe({
      next: (response) => {
        this.isCreatingProduct = false;
        this.productCreated = true;
        this.addMessage('assistant', '¡Producto creado exitosamente! Ya está disponible en tu tienda.');
        console.log('Product created:', response);
      },
      error: (error) => {
        this.isCreatingProduct = false;
        console.error('Error creating product:', error);
        this.addMessage('assistant', 'Hubo un error al crear el producto. Por favor, intenta nuevamente.');
      }
    });
  }

  resetConversation(): void {
    this.messages = [];
    this.productName = '';
    this.detectedCategory = null;
    this.templateFields = [];
    this.currentFieldIndex = 0;
    this.collectedData = {};
    this.currentQuestion = '';
    this.isCreatingProduct = false;
    this.productCreated = false;
    this.startConversation();
  }
}
