import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-category-icon',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './category-icon.html',
  styles: [`
    :host {
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
  `]
})
export class CategoryIconComponent {
  @Input() slug: string = '';
  @Input() iconClass: string = '';

  get normalizedSlug(): string {
    return (this.slug || '').toLowerCase().trim();
  }
}
