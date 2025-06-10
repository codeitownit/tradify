import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/dashboard.dart';
import 'services/api_service.dart';
import 'services/socket_service.dart';
import 'screens/configuration.dart';
import 'screens/analytics.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ApiService()),
        ChangeNotifierProvider(create: (_) => SocketService()),
      ],
      child: const TradingBotApp(),
    ),
  );
}

class TradingBotApp extends StatelessWidget {
  const TradingBotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'XGBoost Trading Bot',
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const DashboardScreen(),
      routes: {
        '/config': (context) => const ConfigurationScreen(),
        '/analytics': (context) => const AnalyticsScreen(),
      },
    );
  }
}