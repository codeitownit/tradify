import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class ConfigurationScreen extends StatelessWidget {
  const ConfigurationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = Provider.of<ApiService>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bot Configuration'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            _buildSwitchTile(
              'Auto Trading',
              apiService.autoTradingEnabled,
              (value) => apiService.setAutoTrading(value),
            ),
            _buildSliderTile(
              'Risk Percentage',
              apiService.riskPercentage,
              (value) => apiService.setRiskPercentage(value),
              0.1,
              5.0,
            ),
            _buildTextField(
              'MT5 Account',
              apiService.mt5Account,
              (value) => apiService.setMt5Account(value),
            ),
            // Add more configuration options
          ],
        ),
      ),
    );
  }

  Widget _buildSwitchTile(String title, bool value, Function(bool) onChanged) {
    return SwitchListTile(
      title: Text(title),
      value: value,
      onChanged: onChanged,
    );
  }

  Widget _buildSliderTile(String title, double value, Function(double) onChanged, double min, double max) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$title: ${value.toStringAsFixed(1)}%'),
        Slider(
          value: value,
          min: min,
          max: max,
          divisions: (max - min).toInt() * 10,
          label: '${value.toStringAsFixed(1)}%',
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _buildTextField(String label, String value, Function(String) onChanged) {
    return TextField(
      decoration: InputDecoration(labelText: label),
      controller: TextEditingController(text: value),
      onChanged: onChanged,
    );
  }
}