import 'package:flutter/material.dart';

class TradeCard extends StatelessWidget {
  final Map<String, dynamic> trade;

  const TradeCard({super.key, required this.trade});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ListTile(
        leading: Icon(
          trade['direction'] == 'long' ? Icons.trending_up : Icons.trending_down,
          color: trade['direction'] == 'long' ? Colors.green : Colors.red,
        ),
        title: Text('${trade['symbol']} - ${trade['lotSize']} lots'),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Entry: ${trade['entryPrice']}'),
            Text('Current: ${trade['currentPrice']}'),
            Text('P/L: \$${trade['profitLoss']}'),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () {
            // Close trade logic
          },
        ),
      ),
    );
  }
}