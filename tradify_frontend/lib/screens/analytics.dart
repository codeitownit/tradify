import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';

class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = Provider.of<ApiService>(context);
    final performanceData = apiService.performanceData;

    // final spots = performanceData.map((data) => FlSpot(
    //       data['time'].millisecondsSinceEpoch.toDouble(),
    //       data['value'],
    //     )).toList();
    
    final spots = performanceData.map((data) {
      final time = DateTime.parse(data['time']); // Parse the ISO 8601 string
      final value = (data['value'] is num)
          ? data['value'].toDouble()
          : double.tryParse(data['value'].toString()) ?? 0.0;
      return FlSpot(
        time.millisecondsSinceEpoch.toDouble(),
        value,
      );
    }).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Trading Analytics')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: LineChart(
          LineChartData(
            lineBarsData: [
              LineChartBarData(
                spots: spots,
                isCurved: true,
                color: Colors.blue,
                barWidth: 4,
                belowBarData: BarAreaData(show: false),
                dotData: FlDotData(show: false),
              ),
            ],
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
                sideTitles: SideTitles(
                  showTitles: true,
                ),
              ),
              topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
              rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            ),
            borderData: FlBorderData(show: true),
            gridData: FlGridData(show: true),
            minX: spots.isNotEmpty ? spots.first.x : 0,
            maxX: spots.isNotEmpty ? spots.last.x : 0,
          ),
        ),
      ),
    );
  }
}