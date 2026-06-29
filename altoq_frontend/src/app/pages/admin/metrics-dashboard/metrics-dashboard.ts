import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AdminMetricsService, AdminMetricsSummary, AdminMetricChartPoint, AdminStoreRanking } from '../../../services/admin-metrics';

@Component({
  selector: 'app-metrics-dashboard',
  imports: [CommonModule, RouterLink],
  templateUrl: './metrics-dashboard.html',
  styleUrl: './metrics-dashboard.css'
})
export class MetricsDashboard implements OnInit {
  summary: AdminMetricsSummary | null = null;
  charts: AdminMetricChartPoint[] = [];
  rankings: AdminStoreRanking[] = [];
  isLoading = true;
  daysPeriod = 30;

  // Configuración de gráficos SVG
  svgPoints: any[] = [];
  revenuePath = '';
  revenueFillPath = '';
  ordersPath = '';
  ordersFillPath = '';
  chatsPath = '';
  chatsFillPath = '';
  usersPath = '';
  usersFillPath = '';

  chartMaxRevenue = 0;
  chartMaxOrders = 0;
  chartMaxChats = 0;
  chartMaxUsers = 0;

  yAxisLabelsRevenue: number[] = [];
  yAxisLabelsChats: number[] = [];

  // Control del Tooltip
  hoveredPoint: any = null;
  hoveredPointType: 'sales' | 'chats' | null = null;
  tooltipX = 0;
  tooltipY = 0;

  constructor(private metricsService: AdminMetricsService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Consultar KPIs generales
    this.metricsService.getSummary().subscribe({
      next: (summary) => {
        this.summary = summary;
      },
      error: (err) => {
        console.error('Error al cargar resumen:', err);
      }
    });

    // Consultar datos de gráficos
    this.metricsService.getCharts(this.daysPeriod).subscribe({
      next: (charts) => {
        this.charts = charts;
        this.calculateSvgPoints();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error al cargar gráficos:', err);
        this.isLoading = false;
      }
    });

    // Consultar ranking de tiendas
    this.metricsService.getRankings(5).subscribe({
      next: (rankings) => {
        this.rankings = rankings;
      },
      error: (err) => {
        console.error('Error al cargar rankings:', err);
      }
    });
  }

  changePeriod(days: number): void {
    this.daysPeriod = days;
    this.isLoading = true;
    this.metricsService.getCharts(days).subscribe({
      next: (charts) => {
        this.charts = charts;
        this.calculateSvgPoints();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error al cambiar de período:', err);
        this.isLoading = false;
      }
    });
  }

  // Cálculos matemáticos para escalar puntos y trazar curvas SVG
  calculateSvgPoints(): void {
    const w = 600;
    const h = 220;
    const padL = 60;
    const padR = 20;
    const padT = 20;
    const padB = 40;

    const count = this.charts.length;
    this.svgPoints = [];
    
    if (count < 2) {
      this.revenuePath = '';
      this.revenueFillPath = '';
      this.ordersPath = '';
      this.ordersFillPath = '';
      this.chatsPath = '';
      this.chatsFillPath = '';
      this.usersPath = '';
      this.usersFillPath = '';
      return;
    }

    const revenues = this.charts.map(c => c.revenue);
    const ordersList = this.charts.map(c => c.orders);
    const chatsList = this.charts.map(c => c.chats);
    const usersList = this.charts.map(c => c.new_users);

    const maxRevenue = Math.max(...revenues, 10);
    const maxOrders = Math.max(...ordersList, 5);
    const maxChats = Math.max(...chatsList, 5);
    const maxUsers = Math.max(...usersList, 5);

    this.chartMaxRevenue = maxRevenue;
    this.chartMaxOrders = maxOrders;
    this.chartMaxChats = maxChats;
    this.chartMaxUsers = maxUsers;

    // Etiquetas del eje Y (5 niveles equidistantes)
    this.yAxisLabelsRevenue = [
      maxRevenue,
      maxRevenue * 0.75,
      maxRevenue * 0.5,
      maxRevenue * 0.25,
      0
    ];

    this.yAxisLabelsChats = [
      maxChats,
      maxChats * 0.75,
      maxChats * 0.5,
      maxChats * 0.25,
      0
    ];

    let revPath = '';
    let ordPath = '';
    let chatPath = '';
    let userPath = '';

    for (let i = 0; i < count; i++) {
      const data = this.charts[i];
      const x = padL + (i * (w - padL - padR)) / (count - 1);

      // Escalar coordenadas en base al tamaño de la caja del SVG
      const yRevenue = h - padB - (data.revenue / maxRevenue) * (h - padT - padB);
      const yOrders = h - padB - (data.orders / maxOrders) * (h - padT - padB);
      const yChats = h - padB - (data.chats / maxChats) * (h - padT - padB);
      const yUsers = h - padB - (data.new_users / maxUsers) * (h - padT - padB);

      this.svgPoints.push({
        x,
        yRevenue,
        yOrders,
        yChats,
        yUsers,
        data,
        formattedDate: this.formatDateLabel(data.date)
      });

      if (i === 0) {
        revPath = `M ${x} ${yRevenue}`;
        ordPath = `M ${x} ${yOrders}`;
        chatPath = `M ${x} ${yChats}`;
        userPath = `M ${x} ${yUsers}`;
      } else {
        revPath += ` L ${x} ${yRevenue}`;
        ordPath += ` L ${x} ${yOrders}`;
        chatPath += ` L ${x} ${yChats}`;
        userPath += ` L ${x} ${yUsers}`;
      }
    }

    this.revenuePath = revPath;
    this.ordersPath = ordPath;
    this.chatsPath = chatPath;
    this.usersPath = userPath;

    // Completar caminos para el área rellena con gradiente (cierra el polígono en la línea base)
    this.revenueFillPath = `${revPath} L ${this.svgPoints[count - 1].x} ${h - padB} L ${this.svgPoints[0].x} ${h - padB} Z`;
    this.ordersFillPath = `${ordPath} L ${this.svgPoints[count - 1].x} ${h - padB} L ${this.svgPoints[0].x} ${h - padB} Z`;
    this.chatsFillPath = `${chatPath} L ${this.svgPoints[count - 1].x} ${h - padB} L ${this.svgPoints[0].x} ${h - padB} Z`;
    this.usersFillPath = `${userPath} L ${this.svgPoints[count - 1].x} ${h - padB} L ${this.svgPoints[0].x} ${h - padB} Z`;
  }

  formatDateLabel(dateStr: string): string {
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      return `${parts[2]}/${parts[1]}`; // Retornar DD/MM
    }
    return dateStr;
  }

  // Lógica interactiva para mostrar el tooltip encima del punto sobrevolado
  showTooltip(event: MouseEvent, point: any, type: 'sales' | 'chats'): void {
    this.hoveredPoint = point;
    this.hoveredPointType = type;
    
    const target = event.currentTarget as SVGElement;
    const rect = target.getBoundingClientRect();
    const parentEl = target.closest('.chart-card');
    
    if (parentEl) {
      const parentRect = parentEl.getBoundingClientRect();
      this.tooltipX = rect.left - parentRect.left + rect.width / 2;
      this.tooltipY = rect.top - parentRect.top - 65; // Colocar 65px arriba del punto
    } else {
      this.tooltipX = event.clientX;
      this.tooltipY = event.clientY - 65;
    }
  }

  hideTooltip(): void {
    this.hoveredPoint = null;
    this.hoveredPointType = null;
  }
}
