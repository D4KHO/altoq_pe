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

  createdProductId: number | null = null;
  awaitingImage: boolean = false;
  imageInputMode: 'choice' | 'upload' | 'url' = 'choice';
  inputImageUrl: string = '';
  isUploading: boolean = false;

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
          let replyText = response.reply;
          if (replyText.includes('[REQUEST_IMAGE]')) {
            replyText = replyText.replace('[REQUEST_IMAGE]', '').trim();
            this.awaitingImage = true;
            this.imageInputMode = 'choice';
          }
          if (replyText) {
            this.addMessage('assistant', replyText);
          }
        }

        if (response.product_created) {
          this.finishProductCreation();
        } else {
          this.scrollToBottom();
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
    this.awaitingImage = false;
    this.createdProductId = null;
    this.imageInputMode = 'choice';
    this.inputImageUrl = '';
    this.isUploading = false;
    this.startConversation();
  }

  selectUploadMode(): void {
    this.imageInputMode = 'upload';
    this.scrollToBottom();
  }

  selectUrlMode(): void {
    this.imageInputMode = 'url';
    this.scrollToBottom();
  }

  cancelImageStep(): void {
    this.awaitingImage = false;
    this.handleUserInput('Quiero omitir la imagen. Usa la imagen por defecto.');
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (!file) return;

    this.isUploading = true;
    const formData = new FormData();
    formData.append('file', file);

    this.sellerService.uploadTempImage(formData).subscribe({
      next: (res) => {
        this.isUploading = false;
        this.awaitingImage = false;
        this.handleUserInput(`He subido esta imagen:\n![Imagen del Producto](${res.image_url})`);
      },
      error: (err) => {
        console.error('Error uploading image', err);
        this.isUploading = false;
        this.addMessage('assistant', 'Hubo un error al subir la imagen. Por favor, intenta de nuevo o prueba con una URL.');
        this.imageInputMode = 'choice';
      }
    });
  }

  saveImageUrl(): void {
    if (!this.inputImageUrl.trim()) return;

    const url = this.inputImageUrl;
    this.isUploading = false;
    this.awaitingImage = false;
    this.inputImageUrl = '';
    
    this.handleUserInput(`He subido esta imagen:\n![Imagen del Producto](${url})`);
  }

  finishProductCreation(): void {
    this.awaitingImage = false;
    this.addMessage('assistant', '¡El producto ha sido publicado exitosamente en tu tienda! Redirigiendo...');
    setTimeout(() => {
      this.productCreatedEvent.emit();
    }, 2500);
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
      }
    }, 100);
  }
}
