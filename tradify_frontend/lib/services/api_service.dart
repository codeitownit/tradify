// api_service.dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService extends ChangeNotifier {
  bool _autoTradingEnabled = true;
  double _riskPercentage = 2.0;
  String _mt5Account = '';
  List<Map<String, dynamic>> _activeTrades = [];
  Map<String, dynamic> _tradeStats = {};
  final Map<String, List<Map<String, dynamic>>> _chartData = {};
  late List<Map<String, dynamic>> performanceData;
  final String _apiUrl = 'http://localhost:5000';

  bool get autoTradingEnabled => _autoTradingEnabled;
  double get riskPercentage => _riskPercentage;
  String get mt5Account => _mt5Account;
  List<Map<String, dynamic>> get activeTrades => _activeTrades;
  Map<String, dynamic> get tradeStats => _tradeStats;
  
  List<Map<String, dynamic>> getChartData(String symbol) {
    return _chartData[symbol] ?? [];
  }
   bool _isLoading = true;
bool get isLoading => _isLoading;

  Future<void> fetchInitialData() async {
     _isLoading = true;
  notifyListeners();
    try {
      // Fetch active trades
      final tradesResponse = await http.get(Uri.parse('$_apiUrl/api/trades'));

if (tradesResponse.statusCode == 200) {
  final decoded = json.decode(tradesResponse.body);
final tradesData = decoded['data'];

if (tradesData is List) {
  _activeTrades = List<Map<String, dynamic>>.from(tradesData);
  print('Active trades loaded: $_activeTrades');
} else {
  _activeTrades = [];
}

}


      // Fetch trade stats
      final statsResponse = await http.get(Uri.parse('$_apiUrl/api/stats'));
      if (statsResponse.statusCode == 200) {
        _tradeStats = Map<String, dynamic>.from(json.decode(statsResponse.body));
      }

      // Fetch chart data
      for (var symbol in ['EURUSD', 'GBPUSD']) {
        final chartResponse = await http.get(Uri.parse('$_apiUrl/api/chart/$symbol'));
        if (chartResponse.statusCode == 200) {
          _chartData[symbol] = List<Map<String, dynamic>>.from(json.decode(chartResponse.body));
        }
      }
 performanceData = _generatePerformanceData();

      notifyListeners();
    } catch (e) {
      print('Error fetching data: $e');
    }
    finally {
    _isLoading = false;
    notifyListeners();
  }
  }
 List<Map<String, dynamic>> _generatePerformanceData() {
  final now = DateTime.now();
  return List.generate(100, (index) {
    final value = 100.0 + (index % 20) * 0.5;
    return {
      'time': now.subtract(Duration(minutes: 15 * (100 - index))),
      'value': value,
    };
  });
}
Future<bool> isSymbolAvailable(String symbol) async {
  try {
    final response = await http.get(Uri.parse('$_apiUrl/api/chart/$symbol'));
    return response.statusCode == 200;
  } catch (_) {
    return false;
  }
}

  Future<void> updateConfig(Map<String, dynamic> config) async {
    try {
      final response = await http.post(
        Uri.parse('$_apiUrl/api/config'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(config),
      );

      if (response.statusCode == 200) {
        if (config.containsKey('autoTrading')) {
          _autoTradingEnabled = config['autoTrading'];
        }
        if (config.containsKey('riskPercentage')) {
          _riskPercentage = config['riskPercentage'];
        }
        if (config.containsKey('mt5Account')) {
          _mt5Account = config['mt5Account'];
        }
        notifyListeners();
      }
    } catch (e) {
      print('Error updating config: $e');
    }
  }

  void setAutoTrading(bool value) {
    _autoTradingEnabled = value;
    updateConfig({'autoTrading': value});
    notifyListeners();
  }

  void setRiskPercentage(double value) {
    _riskPercentage = value;
    updateConfig({'riskPercentage': value});
    notifyListeners();
  }

  void setMt5Account(String value) {
    _mt5Account = value;
    updateConfig({'mt5Account': value});
    notifyListeners();
  }
}