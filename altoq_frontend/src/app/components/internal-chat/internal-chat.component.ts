import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ChatService } from '../../services/chat.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-internal-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './internal-chat.component.html',
  styleUrls: ['./internal-chat.component.css']
})
export class InternalChatComponent implements OnInit {
  chatId: number | null = null;
  productId: number | null = null;
  sellerId: number | null = null;
  messages: any[] = [];
  newMessage: string = '';
  currentUserId: number = 1; // This should come from auth service
  isLoading: boolean = false;
  chatInfo: any = null;

  constructor(
    private route: ActivatedRoute,
    private chatService: ChatService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.chatId = params['chatId'] ? +params['chatId'] : null;
      this.productId = params['productId'] ? +params['productId'] : null;
      this.sellerId = params['sellerId'] ? +params['sellerId'] : null;

      if (this.chatId) {
        this.loadChat(this.chatId);
      } else if (this.productId && this.sellerId) {
        this.startNewChat();
      }
    });
  }

  startNewChat(): void {
    if (this.productId && this.sellerId) {
      this.isLoading = true;
      this.chatService.startChat(this.sellerId, this.productId).subscribe({
        next: (chat) => {
          this.chatId = chat.id;
          this.chatInfo = chat;
          this.loadMessages(chat.id);
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error starting chat:', error);
          this.isLoading = false;
        }
      });
    }
  }

  loadChat(chatId: number): void {
    this.isLoading = true;
    this.chatService.getChat(chatId).subscribe({
      next: (chat) => {
        this.chatInfo = chat;
        this.loadMessages(chatId);
      },
      error: (error) => {
        console.error('Error loading chat:', error);
        this.isLoading = false;
      }
    });
  }

  loadMessages(chatId: number): void {
    this.chatService.getChatMessages(chatId).subscribe({
      next: (messages) => {
        this.messages = messages;
        this.scrollToBottom();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading messages:', error);
        this.isLoading = false;
      }
    });
  }

  sendMessage(): void {
    if (this.newMessage.trim() && this.chatId) {
      const messageContent = this.newMessage;
      this.newMessage = '';

      // Optimistically add message to UI
      this.messages.push({
        sender_id: this.currentUserId,
        content: messageContent,
        created_at: new Date(),
        is_read: false
      });

      this.chatService.sendMessage(this.chatId, messageContent).subscribe({
        next: (message) => {
          // Update the message with server response
          const index = this.messages.length - 1;
          this.messages[index] = message;
          this.scrollToBottom();
        },
        error: (error) => {
          console.error('Error sending message:', error);
          // Remove the optimistic message on error
          this.messages.pop();
          
          // Mostrar mensaje de error del backend (como la alerta de seguridad) en el Toast
          const errorMsg = error.error?.detail || 'No se pudo enviar el mensaje.';
          this.toastService.show(errorMsg, 'error');
        }
      });
    }
  }

  scrollToBottom(): void {
    setTimeout(() => {
      const chatContainer = document.getElementById('chatMessages');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 100);
  }

  closeChat(): void {
    if (this.chatId && confirm('¿Estás seguro de que deseas cerrar este chat?')) {
      this.chatService.closeChat(this.chatId).subscribe({
        next: () => {
          alert('Chat cerrado exitosamente');
          // Navigate back or handle accordingly
        },
        error: (error) => {
          console.error('Error closing chat:', error);
        }
      });
    }
  }

  isMyMessage(message: any): boolean {
    return message.sender_id === this.currentUserId;
  }

  formatTime(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
}
