import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class SocketService extends ChangeNotifier {
  WebSocketChannel? _channel;
  bool _isConnected = false;
  List<Map<String, dynamic>> _realTimeData = [];

  bool get isConnected => _isConnected;
  List<Map<String, dynamic>> get realTimeData => _realTimeData;

  Future<void> connect() async {
    try {
      _channel = WebSocketChannel.connect(
        Uri.parse('wss://localhost:5000/ws'),
      );
      
      _channel!.stream.listen(
        (data) {
          _processData(data);
          notifyListeners();
        },
        onError: (error) {
          _isConnected = false;
          notifyListeners();
        },
        onDone: () {
          _isConnected = false;
          notifyListeners();
        },
      );
      
      _isConnected = true;
      notifyListeners();
    } catch (e) {
      _isConnected = false;
      notifyListeners();
    }
  }

  void _processData(dynamic data) {
    // Parse incoming WebSocket data
    // Add to _realTimeData
  }

  void disconnect() {
    _channel?.sink.close();
    _isConnected = false;
    notifyListeners();
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}