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
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error al cambiar de período:', err);
        this.isLoading = false;
      }
    });
  }
}
