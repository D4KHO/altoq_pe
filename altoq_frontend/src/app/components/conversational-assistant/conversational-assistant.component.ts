import { Component, OnInit, Output, EventEmitter, Input, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SellerService } from '../../services/seller.service';
import { MarkdownFormatPipe } from '../../pipes/markdown-format.pipe';

@Component({
  selector: 'app-conversational-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule, MarkdownFormatPipe],
  templateUrl: './conversational-assistant.component.html',
  styleUrls: ['./conversational-assistant.component.css']
})
export class ConversationalAssistantComponent implements OnInit {
  messages: { sender: 'user' | 'assistant'; content: string }[] = [];
  userInput: string = '';
  isTyping: boolean = false;
  isCreatingProduct: boolean = false;

  @Input() storeId: number | null = null;
  @Input() storeName: string = '';
  @Output() productCreatedEvent = new EventEmitter<void>();

  @ViewChild('chatContainer') private chatContainer!: ElementRef;

  constructor(private sellerService: SellerService) {}

  ngOnInit(): void {
    console.log('Product AI Assistant initialized');
    this.startConversation();
  }

  startConversation(): void {
    this.messages = [];
    this.addMessage('assistant', '¡Hola! Soy tu asistente de inteligencia artificial para ayudarte a crear productos. Cuéntame, ¿qué producto deseas vender hoy en tu tienda?');
  }

  addMessage(sender: 'user' | 'assistant', content: string): void {
    this.messages.push({ sender, content });
    this.scrollToBottom();
  }

  handleUserInput(input: string): void {
    if (!input || input.trim() === '') return;
    
    this.addMessage('user', input);
    this.isTyping = true;
    this.isCreatingProduct = true;

    // Call the backend AI endpoint
    this.sellerService.chatWithAiProductAssistant(this.messages).subscribe({
      next: (response) => {
        this.isTyping = false;
        this.isCreatingProduct = false;
        
        if (response.reply) {
          this.addMessage('assistant', response.reply);
        }

        if (response.product_created) {
          setTimeout(() => {
            this.productCreatedEvent.emit();
          }, 2000);
        }
      },
      error: (err) => {
        console.error('Error in AI chat:', err);
        this.isTyping = false;
        this.isCreatingProduct = false;
        this.addMessage('assistant', 'Ups, ocurrió un error al comunicarme con mi servidor central. Por favor, intenta de nuevo.');
      }
    });
  }

  resetConversation(): void {
    this.startConversation();
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
      }
    }, 100);
  }
}
