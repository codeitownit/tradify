import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/chart_widget.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ApiService>(context, listen: false).fetchInitialData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final apiService = Provider.of<ApiService>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Trading Bot Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.pushNamed(context, '/config'),
          ),
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: () => Navigator.pushNamed(context, '/analytics'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => apiService.fetchInitialData(),
        child: ListView(
          children: [
            const ChartWidget(symbol: 'EURUSD'),
            FutureBuilder<bool>(
              future: apiService.isSymbolAvailable('GBPUSD'),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError || !snapshot.data!) {
                  return const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Text(
                      'GBPUSD chart is not available on your account.',
                      style: TextStyle(color: Colors.red),
                    ),
                  );
                }
                return const ChartWidget(symbol: 'GBPUSD');
              },
            ),
            const SizedBox(height: 20),
            if (apiService.activeTrades.isNotEmpty)
              ...apiService.activeTrades.map((trade) => ListTile(
                    title: Text(trade['symbol']),
                    subtitle:
                        Text('${trade['direction']} @ ${trade['entryPrice']}'),
                  )),
            if (apiService.activeTrades.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 40),
                child: Center(child: Text('No active trades')),
              ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showManualTradeDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  void _showManualTradeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Manual Trade'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField(
              items: ['EURUSD', 'GBPUSD'].map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
              onChanged: (value) {},
              decoration: const InputDecoration(labelText: 'Symbol'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              // Execute manual trade
              Navigator.pop(context);
            },
            child: const Text('Execute'),
          ),
        ],
      ),
    );
  }
}
