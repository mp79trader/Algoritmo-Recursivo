import React from 'react'
import { Card } from '../components/common/Card'
import { FileText, Code, Activity, Shield, HelpCircle, BookOpen, TrendingUp, Database, Zap, AlertCircle } from 'lucide-react'

export function Documentation() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          <span className="text-accent-gold">Documentación Técnica</span>
        </h1>
        <p className="text-text-secondary text-lg max-w-2xl mx-auto">
          Guía completa sobre el funcionamiento, implementación y uso del algoritmo de Transformada Rápida de Fourier (FFT) Recursiva en mercados financieros.
        </p>
      </div>

      {/* Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <NavCard 
          icon={BookOpen} 
          title="Fundamentos" 
          desc="Bases matemáticas de la Transformada de Fourier y el algoritmo Cooley-Tukey."
          href="#fundamentos"
        />
        <NavCard 
          icon={Code} 
          title="Algoritmo" 
          desc="Implementación recursiva y optimizaciones para análisis espectral."
          href="#algoritmo"
        />
        <NavCard 
          icon={Activity} 
          title="Mercados" 
          desc="Aplicación práctica en análisis financiero y detección de ciclos."
          href="#mercados"
        />
        <NavCard 
          icon={Database} 
          title="Fuentes" 
          desc="Diferencia entre fuentes para análisis y trading en vivo."
          href="#fuentes"
        />
        <NavCard 
          icon={Activity} 
          title="Trading en Vivo" 
          desc="Sistema de scalping con detección automática de señales y ejecución de órdenes."
          href="#trading-vivo"
        />
        <NavCard 
          icon={TrendingUp} 
          title="Visualización" 
          desc="Guía sobre los gráficos de predicción, tendencias y datos históricos."
          href="#visualizacion"
        />
        <NavCard 
          icon={Shield} 
          title="Riesgos" 
          desc="Análisis de limitaciones, gestión de riesgos y validación."
          href="#riesgos"
        />
        <NavCard 
          icon={HelpCircle} 
          title="FAQ" 
          desc="Preguntas frecuentes sobre precisión, timeframes y estrategias."
          href="#faq"
        />
      </div>

      {/* Content Sections */}
      <div className="space-y-12">
        
        {/* Fundamentos */}
        <Section id="fundamentos" title="Fundamentos Matemáticos" icon={BookOpen}>
          <div className="prose prose-invert max-w-none">
            <h3 className="text-xl font-semibold text-white mb-4">Transformada de Fourier</h3>
            <p className="text-text-secondary mb-4">
              La Transformada de Fourier (TF) es una herramienta matemática fundamental que descompone una señal en sus componentes de frecuencia fundamentales.
            </p>
            <div className="bg-primary-bg/50 p-4 rounded-lg border border-white/10 mb-4 font-mono text-sm">
              X(k) = Σ x[n] * e^(-i2πkn/N)
            </div>
            <p className="text-text-secondary mb-4">
              La DFT descompone la señal en dos componentes para cada frecuencia k:
            </p>
            <ul className="list-disc list-inside text-text-secondary space-y-2 mb-6">
              <li><strong className="text-white">Parte Real:</strong> Componente en fase con el seno</li>
              <li><strong className="text-white">Parte Imaginaria:</strong> Componente en fase con el coseno</li>
              <li><strong className="text-white">Magnitud:</strong> Fuerza o amplitud de la frecuencia</li>
              <li><strong className="text-white">Fase:</strong> Desplazamiento temporal</li>
            </ul>

            <h3 className="text-xl font-semibold text-white mb-4">Algoritmo Cooley-Tukey</h3>
            <p className="text-text-secondary mb-4">
              Utiliza el principio de "divide y vencerás" para reducir la complejidad computacional de O(n²) a O(n log n):
            </p>
            <ol className="list-decimal list-inside text-text-secondary space-y-2">
              <li><strong className="text-white">Dividir:</strong> Separar la señal en índices pares e impares</li>
              <li><strong className="text-white">Reconquistar:</strong> Calcular DFT recursivamente</li>
              <li><strong className="text-white">Combinar:</strong> Unir resultados usando factores de Twiddle</li>
            </ol>
          </div>
        </Section>

        {/* Algoritmo */}
        <Section id="algoritmo" title="Algoritmo FFT Recursivo" icon={Code}>
          <div className="prose prose-invert max-w-none">
            <p className="text-text-secondary mb-6">
              Nuestra implementación incluye optimizaciones específicas para análisis financiero, incluyendo filtrado adaptativo y reconstrucción de señal.
            </p>
            
            <h3 className="text-xl font-semibold text-white mb-4">Filtrado Adaptativo</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <h4 className="font-bold text-accent-gold mb-2">Por Magnitud</h4>
                <p className="text-sm text-text-secondary">Elimina componentes con magnitud menor al 5% del máximo para reducir ruido.</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <h4 className="font-bold text-accent-gold mb-2">Por Frecuencia</h4>
                <p className="text-sm text-text-secondary">Separa tendencias (baja), ciclos (media) y ruido (alta frecuencia).</p>
              </div>
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <h4 className="font-bold text-accent-gold mb-2">Top-N</h4>
                <p className="text-sm text-text-secondary">Selecciona solo los componentes más dominantes y significativos.</p>
              </div>
            </div>
          </div>
        </Section>

        {/* Mercados */}
        <Section id="mercados" title="Aplicación a Mercados" icon={Activity}>
          <div className="prose prose-invert max-w-none">
            <h3 className="text-xl font-semibold text-white mb-4">Análisis de Ciclos</h3>
            <p className="text-text-secondary mb-6">
              Identificamos patrones repetitivos en diferentes escalas temporales:
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="p-3 text-accent-gold">Período (días)</th>
                    <th className="p-3 text-white">Tipo de Ciclo</th>
                    <th className="p-3 text-text-secondary">Implicación</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b border-white/5">
                    <td className="p-3">10 - 30</td>
                    <td className="p-3">Semanal</td>
                    <td className="p-3 text-text-secondary">Swing Trading Corto</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="p-3">30 - 90</td>
                    <td className="p-3">Mensual</td>
                    <td className="p-3 text-text-secondary">Swing Trading Medio</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="p-3">90 - 180</td>
                    <td className="p-3">Trimestral</td>
                    <td className="p-3 text-text-secondary">Position Trading</td>
                  </tr>
                  <tr>
                    <td className="p-3">{'>'} 180</td>
                    <td className="p-3">Anual</td>
                    <td className="p-3 text-text-secondary">Inversión Largo Plazo</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </Section>

        {/* Fuentes de Datos */}
        <Section id="fuentes" title="Fuentes de Datos" icon={Database}>
          <div className="prose prose-invert max-w-none">
            <p className="text-text-secondary mb-6">
              El sistema utiliza diferentes proveedores según la necesidad de precisión y tiempo de respuesta. Es fundamental entender la distinción entre fuentes de análisis y fuentes de trading.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="p-5 rounded-xl bg-blue-500/5 border border-blue-500/20">
                <h4 className="font-bold text-blue-400 mb-2 flex items-center gap-2">
                  <FileText size={18} />
                  Yahoo Finance (Análisis)
                </h4>
                <p className="text-sm text-text-secondary">
                  Utilizada exclusivamente para el <strong>Análisis Histórico</strong> y el cálculo de la FFT diaria. Proporciona una base sólida de datos para identificar ciclos macro, pero no es apta para scalping debido a su retraso (15+ min).
                </p>
              </div>

              <div className="p-5 rounded-xl bg-green-500/5 border border-green-500/20">
                <h4 className="font-bold text-green-400 mb-2 flex items-center gap-2">
                  <Zap size={18} />
                  MT5 / NinjaTrader (Trading)
                </h4>
                <p className="text-sm text-text-secondary">
                  Fuentes para <strong>Trading en Vivo</strong>. Proporcionan datos OHLC de 1 minuto en tiempo real. Son esenciales para la ejecución de órdenes y la detección de señales de scalping intradía.
                </p>
              </div>
            </div>

            <div className="bg-yellow-500/10 p-4 rounded-lg border border-yellow-500/20">
              <h4 className="text-yellow-500 font-bold mb-1 text-sm flex items-center gap-2">
                <AlertCircle size={16} />
                Regla de Oro
              </h4>
              <p className="text-xs text-text-secondary italic">
                "Los datos de Yahoo Finance son para la estrategia; los datos de la plataforma (MT5/Ninja) son para la ejecución."
              </p>
            </div>
          </div>
        </Section>

        {/* Trading en Vivo */}
        <Section id="trading-vivo" title="Sistema de Trading en Vivo" icon={Activity}>
          <div className="prose prose-invert max-w-none">
            <h3 className="text-xl font-semibold text-white mb-4">Funcionamiento del Sistema</h3>
            <p className="text-text-secondary mb-6">
              El módulo de Trading en Vivo ejecuta análisis FFT cada 5 segundos para detectar oportunidades de scalping intradía con ejecución automática en MT5 o NinjaTrader.
            </p>

            <div className="bg-blue-500/10 p-5 rounded-lg border border-blue-500/30 mb-6">
              <h4 className="text-blue-400 font-bold mb-3 text-lg">Flujo de Procesamiento</h4>
              <ol className="space-y-3 text-sm text-text-secondary">
                <li className="flex gap-3">
                  <span className="font-mono text-accent-gold">1.</span>
                  <span><strong className="text-white">Conexión WebSocket:</strong> Establece conexión en tiempo real (ws://localhost:8001/ws/live/SYMBOL)</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-mono text-accent-gold">2.</span>
                  <span><strong className="text-white">Obtención de Datos:</strong> Recibe precio actual desde MT5/NinjaTrader cada 5 segundos</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-mono text-accent-gold">3.</span>
                  <span><strong className="text-white">Análisis FFT:</strong> Procesa 200 puntos históricos para extraer ciclos, tendencia y confianza</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-mono text-accent-gold">4.</span>
                  <span><strong className="text-white">Detección de Señal:</strong> Evalúa criterios de scalping (período 0.1-3d, confianza ≥60%, fuerza ≥30%)</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-mono text-accent-gold">5.</span>
                  <span><strong className="text-white">Cálculo TP/SL:</strong> Usa ATR (Average True Range) para stop loss dinámico</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-mono text-accent-gold">6.</span>
                  <span><strong className="text-white">Validación:</strong> Verifica Risk:Reward ≥1.5:1 y SL ≤5% del precio</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-mono text-accent-gold">7.</span>
                  <span><strong className="text-white">Ejecución:</strong> Envía orden automática si Auto-Trading está activo</span>
                </li>
              </ol>
            </div>

            <h3 className="text-xl font-semibold text-white mb-4">Criterios de Detección</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <h4 className="font-bold text-green-400 mb-2">Señal BUY</h4>
                <ul className="text-sm text-text-secondary space-y-1">
                  <li>• Tendencia: UP</li>
                  <li>• Fuerza de tendencia: {'>'} 30%</li>
                  <li>• Ciclo: 0.1 - 3.0 días</li>
                  <li>• Confianza: ≥ 60%</li>
                </ul>
              </div>
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <h4 className="font-bold text-red-400 mb-2">Señal SELL</h4>
                <ul className="text-sm text-text-secondary space-y-1">
                  <li>• Tendencia: DOWN</li>
                  <li>• Fuerza de tendencia: {'>'} 30%</li>
                  <li>• Ciclo: 0.1 - 3.0 días</li>
                  <li>• Confianza: ≥ 60%</li>
                </ul>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-white mb-4">Gestión de Riesgo</h3>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="p-3 text-accent-gold">Parámetro</th>
                    <th className="p-3 text-white">Cálculo</th>
                    <th className="p-3 text-text-secondary">Objetivo</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  <tr className="border-b border-white/5">
                    <td className="p-3 font-mono">Stop Loss</td>
                    <td className="p-3">Entry ± (ATR × 1.5)</td>
                    <td className="p-3 text-text-secondary">Protección dinámica por volatilidad</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="p-3 font-mono">Take Profit</td>
                    <td className="p-3">Entry ± (SL_distance × 2.0)</td>
                    <td className="p-3 text-text-secondary">Risk:Reward ratio de 2:1</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="p-3 font-mono">Validación R:R</td>
                    <td className="p-3">Reward / Risk ≥ 1.5</td>
                    <td className="p-3 text-text-secondary">Asegurar rentabilidad mínima</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-mono">Max SL Distance</td>
                    <td className="p-3">≤ 5% del precio</td>
                    <td className="p-3 text-text-secondary">Limitar exposición por operación</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <h3 className="text-xl font-semibold text-white mb-4">Clasificación de Señales</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/30">
                <h4 className="font-bold text-green-400 mb-2">FUERTE</h4>
                <p className="text-sm text-text-secondary">Confianza ≥ 80%</p>
              </div>
              <div className="p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/30">
                <h4 className="font-bold text-yellow-400 mb-2">MODERADA</h4>
                <p className="text-sm text-text-secondary">Confianza 65-79%</p>
              </div>
              <div className="p-4 bg-orange-500/10 rounded-lg border border-orange-500/30">
                <h4 className="font-bold text-orange-400 mb-2">DÉBIL</h4>
                <p className="text-sm text-text-secondary">Confianza 60-64%</p>
              </div>
            </div>

            <div className="bg-yellow-500/10 p-4 rounded-lg border border-yellow-500/20">
              <h4 className="text-yellow-400 font-bold mb-2 text-sm">⚠️ Importante - Auto-Trading</h4>
              <p className="text-xs text-text-secondary mb-2">
                El sistema ejecutará órdenes automáticamente cuando el toggle de Auto-Trading esté activo. Asegúrese de:
              </p>
              <ul className="text-xs text-text-secondary space-y-1 ml-4">
                <li>• Tener conexión activa con MT5 o NinjaTrader</li>
                <li>• Verificar que el símbolo esté disponible en su broker</li>
                <li>• Contar con margen suficiente para operar</li>
                <li>• Monitorear las señales activas regularmente</li>
              </ul>
            </div>
          </div>
        </Section>

        {/* Visualización */}
        <Section id="visualizacion" title="Guía de Visualización" icon={TrendingUp}>
          <div className="prose prose-invert max-w-none">
            <p className="text-text-secondary mb-6">
              El sistema utiliza Plotly.js y Lightweight Charts para representar los datos procesados. Aquí explicamos qué representa cada componente visual:
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="p-5 bg-white/5 rounded-xl border border-white/10">
                <h4 className="font-bold text-blue-400 mb-3 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-400" />
                  Precio Real (Histórico)
                </h4>
                <p className="text-sm text-text-secondary">
                  Representa los datos crudos obtenidos del proveedor (yfinance, MT5 o NinjaTrader). Es la base sobre la cual se calcula la FFT.
                </p>
              </div>

              <div className="p-5 bg-white/5 rounded-xl border border-white/10">
                <h4 className="font-bold text-purple-400 mb-3 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-purple-400" />
                  Señal FFT (Reconstruida)
                </h4>
                <p className="text-sm text-text-secondary">
                  Es la señal filtrada tras aplicar la FFT inversa. Elimina el ruido y resalta los ciclos dominantes que el algoritmo ha identificado como significativos.
                </p>
              </div>

              <div className="p-5 bg-white/5 rounded-xl border border-white/10">
                <h4 className="font-bold text-green-400 mb-3 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                  Tendencia (Baja Frecuencia)
                </h4>
                <p className="text-sm text-text-secondary">
                  Extraída de los componentes de más baja frecuencia. Indica la dirección macro del mercado sin las oscilaciones de corto plazo.
                </p>
              </div>

              <div className="p-5 bg-white/5 rounded-xl border border-white/10">
                <h4 className="font-bold text-accent-gold mb-3 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-accent-gold" />
                  Proyección (Predicción)
                </h4>
                <p className="text-sm text-text-secondary">
                  Extrapolación matemática de los ciclos identificados hacia el futuro. La línea punteada indica la trayectoria más probable según el modelo.
                </p>
              </div>
            </div>

            <div className="bg-blue-500/10 p-4 rounded-lg border border-blue-500/20">
              <h4 className="text-blue-400 font-bold mb-1 text-sm">Nota sobre Carga de Gráficos</h4>
              <p className="text-xs text-text-secondary">
                Si el gráfico aparece vacío o negro, asegúrese de que la conexión al backend esté activa y que el símbolo seleccionado tenga datos históricos disponibles para el periodo solicitado. Puede usar el botón "Intentar Nuevamente" en caso de error de red.
              </p>
            </div>
          </div>
        </Section>

        {/* Riesgos */}
        <Section id="riesgos" title="Análisis de Riesgos" icon={Shield}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-white">Limitaciones del Modelo</h3>
              <ul className="space-y-3">
                <RiskItem title="Estacionariedad" desc="Los mercados no son perfectamente estacionarios. Usamos diferenciación y ventanas deslizantes." />
                <RiskItem title="Eventos Exógenos" desc="FFT no puede predecir noticias o eventos económicos imprevistos." />
                <RiskItem title="Degradación" desc="La precisión de las predicciones disminuye con el horizonte temporal." />
              </ul>
            </div>
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-white">Gestión de Riesgo</h3>
              <ul className="space-y-3">
                <RiskItem title="Stop Loss Dinámico" desc="Ajustado por volatilidad (ATR) para proteger capital." />
                <RiskItem title="Position Sizing" desc="Tamaño de posición calculado basado en riesgo máximo por operación." />
                <RiskItem title="Diversificación" desc="Análisis de correlación para evitar exposición concentrada." />
              </ul>
            </div>
          </div>
        </Section>

        {/* FAQ */}
        <Section id="faq" title="Preguntas Frecuentes" icon={HelpCircle}>
          <div className="space-y-6">
            <FAQItem 
              q="¿Qué tan precisa es la predicción?" 
              a="La precisión direccional suele estar entre 60-70% para futuros de índices a 30 días. La precisión de precio exacto es menor, por lo que recomendamos enfocarse en la tendencia y los ciclos."
            />
            <FAQItem 
              q="¿Cuál es el mejor timeframe?" 
              a="Recomendamos análisis Diario (1d) para swing trading y 4 Horas (4h) para mayor detalle. Timeframes menores a 1h tienen demasiado ruido para FFT."
            />
            <FAQItem 
              q="¿Funciona en mercados bajistas?" 
              a="Sí, FFT analiza patrones cíclicos independientemente de la dirección. La fase de los componentes determina si el ciclo está en una etapa alcista o bajista."
            />
          </div>
        </Section>

      </div>
    </div>
  )
}

function NavCard({ icon: Icon, title, desc, href }) {
  return (
    <a 
      href={href}
      className="p-6 rounded-xl bg-white/5 border border-white/10 hover:border-accent-gold/50 hover:bg-white/10 transition-all duration-300 group"
    >
      <Icon className="w-8 h-8 text-accent-gold mb-4 group-hover:scale-110 transition-transform" />
      <h3 className="text-lg font-bold mb-2">{title}</h3>
      <p className="text-sm text-text-secondary">{desc}</p>
    </a>
  )
}

function Section({ id, title, icon: Icon, children }) {
  return (
    <Card className="p-8" id={id}>
      <div className="flex items-center gap-4 mb-8 pb-4 border-b border-white/10">
        <div className="p-3 rounded-lg bg-accent-gold/10">
          <Icon className="w-6 h-6 text-accent-gold" />
        </div>
        <h2 className="text-2xl font-bold">{title}</h2>
      </div>
      {children}
    </Card>
  )
}

function RiskItem({ title, desc }) {
  return (
    <li className="flex gap-3 items-start p-3 rounded bg-white/5">
      <div className="mt-1 min-w-[6px] h-1.5 rounded-full bg-red-400" />
      <div>
        <strong className="block text-white text-sm mb-1">{title}</strong>
        <span className="text-xs text-text-secondary">{desc}</span>
      </div>
    </li>
  )
}

function FAQItem({ q, a }) {
  return (
    <div className="p-4 rounded-lg bg-white/5 border border-white/5">
      <h4 className="font-bold text-accent-gold mb-2">{q}</h4>
      <p className="text-sm text-text-secondary leading-relaxed">{a}</p>
    </div>
  )
}
