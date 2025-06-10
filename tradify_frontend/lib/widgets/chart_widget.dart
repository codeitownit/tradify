import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';

class ChartWidget extends StatelessWidget {
  final String symbol;
  final bool showIndicators;

  const ChartWidget({
    super.key, 
    required this.symbol,
    this.showIndicators = true,
  });

  @override
  Widget build(BuildContext context) {
    final apiService = Provider.of<ApiService>(context);
    final data = apiService.getChartData(symbol);

    final candleData = data.map((d) => CandleStick(
      time: d['time'],
      open: d['open'],
      high: d['high'],
      low: d['low'],
      close: d['close'],
    )).toList();

    return Card(
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              symbol,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            SizedBox(
              height: 300,
              child: CandleStickChartWidget(
                candleData: candleData,
                showIndicators: showIndicators,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class CandleStickChartWidget extends StatelessWidget {
  final List<CandleStick> candleData;
  final bool showIndicators;

  const CandleStickChartWidget({
    super.key,
    required this.candleData,
    required this.showIndicators,
  });

  @override
  Widget build(BuildContext context) {
    return BarChart(
      BarChartData(
        barGroups: candleData.map((candle) {
          final isBullish = candle.close > candle.open;
          return BarChartGroupData(
            x: candle.time.millisecondsSinceEpoch,
            barRods: [
              BarChartRodData(
                fromY: isBullish ? candle.open : candle.close,
                toY: isBullish ? candle.close : candle.open,
                color: isBullish ? Colors.green : Colors.red,
                width: 8,
                borderRadius: BorderRadius.zero,
              ),
              BarChartRodData(
                fromY: candle.low,
                toY: candle.high,
                color: isBullish ? Colors.green : Colors.red,
                width: 2,
              ),
            ],
          );
        }).toList(),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final date = DateTime.fromMillisecondsSinceEpoch(value.toInt());
                return Text('${date.hour}:${date.minute}');
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: true),
          ),
        ),
        borderData: FlBorderData(show: true),
        gridData: FlGridData(show: true),
        alignment: BarChartAlignment.spaceAround,
      ),
    );
  }
}

class CandleStick {
  final DateTime time;
  final double open;
  final double high;
  final double low;
  final double close;

  CandleStick({
    required this.time,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
  });
}