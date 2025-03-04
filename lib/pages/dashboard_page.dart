import 'package:emu_config/globals.dart';
import 'package:emu_config/emus/emus_provider.dart';
import 'package:emu_config/pages/emus_page.dart';
import 'package:emu_config/pages/gamepads_page.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() {
      setState(() {});
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Emu Config'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Gamepads'),
            Tab(text: 'Emus'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              if (_tabController.index == 0) gamepadService.setCustomGamepadController();
              if (_tabController.index == 1) Provider.of<EmusProvider>(context, listen: false).notifyListeners();
            },
          )
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          GamepadsPage(),
          EmusPage(),
        ],
      ),
    );
  }
}
