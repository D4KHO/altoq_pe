import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Pipe({
  name: 'markdownFormat',
  standalone: true
})
export class MarkdownFormatPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}

  transform(value: string): SafeHtml {
    if (!value) return '';
    
    // Reemplazar **texto** por <strong>texto</strong>
    let formatted = value.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convertir listas con asterisco o guión (ej. * Item) a viñetas (• Item)
    formatted = formatted.replace(/(^|\n)\s*[\*\-]\s+/g, '$1• ');

    // Reemplazar *texto* por <em>texto</em>
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Eliminar cualquier asterisco sobrante por completo
    formatted = formatted.replace(/\*/g, '');
    
    // Asegurarse de mantener los saltos de línea reemplazando \n por <br>
    formatted = formatted.replace(/\n/g, '<br>');

    return this.sanitizer.bypassSecurityTrustHtml(formatted);
  }
}
