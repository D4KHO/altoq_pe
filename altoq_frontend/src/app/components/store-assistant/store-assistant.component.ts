import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SellerService } from '../../services/seller.service';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-store-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './store-assistant.component.html',
  styleUrls: ['./store-assistant.component.css']
})
export class StoreAssistantComponent implements OnInit {
  messages: { sender: string; content: string }[] = [];
  currentQuestion: string = '';
  userInput: string = '';
  storeData: any = {};
  isTyping: boolean = false;
  isCreatingStore: boolean = false;
  storeCreated: boolean = false;

  constructor(
    private sellerService: SellerService,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.startConversation();
  }

  startConversation(): void {
    this.addMessage('assistant', '¡Hola! Soy tu asistente para crear tu tienda en ALTOQ. ¿Cuál es el nombre de tu tienda?');
    this.currentQuestion = 'store_name';
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
      case 'store_name':
        this.storeData.name = input;
        this.addMessage('assistant', '¡Qué buen nombre! ¿Qué tipo de productos vende tu tienda?');
        this.currentQuestion = 'sells';
        break;
      case 'sells':
        this.storeData.sells = input;
        this.addMessage('assistant', 'Perfecto. ¿Cuál es tu RUC?');
        this.currentQuestion = 'ruc';
        break;
      case 'ruc':
        this.storeData.ruc = input;
        this.addMessage('assistant', '¿Cuál es tu número de contacto?');
        this.currentQuestion = 'contact';
        break;
      case 'contact':
        this.storeData.contact = input;
        this.addMessage('assistant', '¿Cuál es tu correo electrónico?');
        this.currentQuestion = 'email';
        break;
      case 'email':
        this.storeData.email = input;
        this.completeConversation();
        break;
    }
  }

  completeConversation(): void {
    this.addMessage('assistant', '¡Perfecto! He recopilado toda la información necesaria para crear tu tienda.');
    
    const summary = this.generateStoreSummary();
    this.addMessage('assistant', `Resumen de tu tienda:\n${summary}\n\n¿Quieres crear tu tienda ahora?`);
    this.currentQuestion = 'confirm_creation';
  }

  generateStoreSummary(): string {
    let summary = `Nombre: ${this.storeData.name}\n`;
    summary += `Vende: ${this.storeData.sells}\n`;
    summary += `RUC: ${this.storeData.ruc}\n`;
    summary += `Contacto: ${this.storeData.contact}\n`;
    summary += `Correo: ${this.storeData.email}\n`;
    return summary;
  }

  createStore(): void {
    const token = this.authService.getToken();
    console.log('Token before creating store:', token);
    
    if (!token) {
      this.addMessage('assistant', 'No tienes una sesión activa. Por favor, inicia sesión primero.');
      return;
    }

    this.isCreatingStore = true;
    this.addMessage('assistant', 'Creando tu tienda...');
    
    const storeData = {
      name: this.storeData.name,
      description: this.storeData.sells,
      ruc: this.storeData.ruc,
      contact: this.storeData.contact,
      email: this.storeData.email
    };

    this.sellerService.becomeSeller(storeData).subscribe({
      next: (response) => {
        this.isCreatingStore = false;
        this.storeCreated = true;
        this.addMessage('assistant', '¡Tienda creada exitosamente! Serás redirigido a tu área de vendedor en unos segundos.');
        console.log('Store created:', response);
        
        setTimeout(() => {
          this.router.navigate(['/seller-area']);
        }, 2000);
      },
      error: (error) => {
        this.isCreatingStore = false;
        console.error('Error creating store:', error);
        this.addMessage('assistant', 'Hubo un error al crear la tienda. Por favor, intenta nuevamente.');
      }
    });
  }

  resetConversation(): void {
    this.messages = [];
    this.storeData = {};
    this.currentQuestion = '';
    this.isCreatingStore = false;
    this.storeCreated = false;
    this.startConversation();
  }
}
