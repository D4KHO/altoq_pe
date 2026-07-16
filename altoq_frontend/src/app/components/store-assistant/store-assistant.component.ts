import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SellerService } from '../../services/seller.service';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MarkdownFormatPipe } from '../../pipes/markdown-format.pipe';

@Component({
  selector: 'app-store-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule, MarkdownFormatPipe],
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
  
  private chatSubscription: any = null;

  constructor(
    private sellerService: SellerService,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.startConversation();
  }

  startConversation(): void {
    // Send an initial "hola" from the user to trigger the AI greeting
    if (this.chatSubscription) {
      this.chatSubscription.unsubscribe();
    }
    
    this.isTyping = true;
    this.chatSubscription = this.sellerService.chatWithAiStoreAssistant([
      { sender: 'user', content: 'Hola, quiero crear mi tienda' }
    ]).subscribe({
      next: (response) => {
        this.isTyping = false;
        this.addMessage('assistant', response.reply);
        this.currentQuestion = 'ai_chat';
      },
      error: (error) => {
        this.isTyping = false;
        console.error('Error starting AI conversation:', error);
        this.addMessage('assistant', '¡Hola! Soy tu asistente para crear tu tienda en ALTOQ. ¿Cuál es el nombre de tu tienda?');
        this.currentQuestion = 'ai_chat';
      }
    });
  }

  addMessage(sender: string, content: string): void {
    this.messages.push({ sender, content });
  }

  handleUserInput(input: string): void {
    if (!input || input.trim() === '') return;
    
    this.addMessage('user', input);
    this.isTyping = true;

    if (this.chatSubscription) {
      this.chatSubscription.unsubscribe();
    }

    // Send full conversation history to the AI backend
    this.chatSubscription = this.sellerService.chatWithAiStoreAssistant(this.messages).subscribe({
      next: (response) => {
        this.isTyping = false;
        this.addMessage('assistant', response.reply);

        if (response.store_created) {
          this.storeCreated = true;
          this.isCreatingStore = false;
          this.currentQuestion = 'completed';
          // Refresh user profile so has_store and role are updated in the navbar
          this.authService.refreshCurrentUser().subscribe();
          setTimeout(() => {
            this.router.navigate(['/seller-area']);
          }, 3000);
        }
      },
      error: (error) => {
        this.isTyping = false;
        console.error('Error communicating with AI:', error);
        this.addMessage('assistant', 'Hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.');
      }
    });
  }

  // Keep createStore for the confirm button in the template (fallback)
  createStore(): void {
    if (this.messages.length > 0) {
      this.isCreatingStore = true;
      this.addMessage('user', 'Sí, confirmo. Crea mi tienda.');
      this.isTyping = true;

      this.sellerService.chatWithAiStoreAssistant(this.messages).subscribe({
        next: (response) => {
          this.isTyping = false;
          this.isCreatingStore = false;
          this.addMessage('assistant', response.reply);

          if (response.store_created) {
            this.storeCreated = true;
            this.currentQuestion = 'completed';
            // Refresh user profile so has_store and role are updated in the navbar
            this.authService.refreshCurrentUser().subscribe();
            setTimeout(() => {
              this.router.navigate(['/seller-area']);
            }, 3000);
          }
        },
        error: (error) => {
          this.isTyping = false;
          this.isCreatingStore = false;
          console.error('Error creating store via AI:', error);
          this.addMessage('assistant', 'Hubo un error al crear la tienda. Por favor, intenta nuevamente.');
        }
      });
    }
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
