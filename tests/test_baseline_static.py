from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "monitor.py"


def test_refactor_copy_declares_v369() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'VERSION_SCRIPT = "369.0"' in source
    assert "Script v369.0" in source


def test_refactor_copy_uses_current_project_commands() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "monitor_galicia_tiempo_real_v45.py" not in source
    assert "requirements_monitor_galicia_v41.txt" not in source
    assert "monitor.py" in source
    assert "requirements.txt" in source


def test_main_market_tabs_keep_compact_without_legacy_tabs() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'self.notebook.add(self.tab_compacta, text="Compacta")' in source
    assert 'self.notebook.add(self.tab_calls, text="Calls")' not in source
    assert 'self.notebook.add(self.tab_puts, text="Puts")' not in source
    assert 'self.notebook.add(self.tab_acciones, text="Acciones")' not in source
    assert 'self.notebook.add(self.tab_futuros, text="Futuros")' not in source


def test_ratios_replaces_matrix_bases_tab() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'self.notebook.add(self.tab_ratios, text="Ratios")' in source
    assert 'self.notebook.add(self.tab_matriz_bases, text="Matriz bases")' not in source
    assert "Vista Cuadro" in source
    assert "Vista Cadena" in source


def test_backtest_keeps_only_coverage_tab_visible() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'self.notebook.add(self.tab_backtest, text="Backtest intrad' not in source
    assert 'self.notebook.add(self.tab_backtest_hedge, text="Backtest cobertura")' in source
    assert 'self.notebook.add(self.tab_backtest_vencimiento, text="Backtest vencimiento")' not in source


def test_smile_vi_keeps_curve_without_surface_tab() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'self.notebook.add(self.tab_smile, text="Smile VI")' in source
    assert "construir_datos_smile" in source
    assert 'self.notebook_smile.add(self.tab_smile_surface, text="Superficie cierres")' not in source


def test_subviews_capacity_is_preserved_from_saved_state() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "self.MAX_SUBVISTAS = 24" in source
    assert "self.SUBVISTAS_INICIALES = 6" in source
    assert "self._resolver_subvistas_activas_guardadas(payload)" in source
    assert "def _subvista_tiene_config_guardada" in source


def test_view_switch_refresh_is_deferred() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "delay_real = max(int(delay_ms), 250)" in source
    assert "cooldown_ms=max(delay_real, 450)" in source


def test_offline_refresh_loop_is_slower() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "if self.offline_mode:" in source
    assert "return 5000" in source
    assert "return 3000" in source


def test_focus_recovery_defers_heavy_refresh() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'self.root.bind("<FocusIn>", self._al_recuperar_foco_ventana, add="+")' in source
    assert "def _al_recuperar_foco_ventana" in source
    assert "cooldown_ms=1000" in source


def test_startup_pumps_tk_events_while_building_views() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "def _bombear_tk_arranque" in source
    assert "self._startup_building_ui = True" in source
    assert "self._startup_building_ui = False" in source
    assert "self._bombear_tk_arranque(forzar=True)" in source


def test_subviews_are_created_lazily() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "def _crear_subvista_perezosa" in source
    assert "def _asegurar_subvista_construida" in source
    assert 'if bool(getattr(self, "_startup_building_ui", False)):' in source
    assert 'self._crear_subvista_perezosa(self.notebook_comp, "notebook_comp", slot, self._crear_vista_comp)' in source
    assert 'self._crear_subvista_perezosa(self.notebook_backtest_hedge, "notebook_backtest_hedge", slot, self._crear_subvista_backtest_hedge)' in source


def test_ui_state_persists_current_views_and_controls() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"vencimiento_general": self.var_vencimiento.get().strip()' in source
    assert '"tabla_relaciones": {' in source
    assert '"backtest_cobertura": {' in source
    assert '"tab_activa": self._tab_smile_activa_indice()' in source
    assert "self._restaurar_tab_principal_guardada_inicio(payload)" in source
    assert "self._programar_hidratacion_de_pestana_principal_activa()" in source


def test_ui_state_persists_subview_layout_and_relation_table_widths() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"subvistas_activas": int(self._subvistas_activas)' in source
    assert '"tab_principal_activa_id"' in source
    assert "return max(1, min(guardadas, max_subvistas))" in source
    assert "sync_column_widths_from_widget" in source
    assert '"anchos_columnas_diaria"' in source
    assert '"anchos_columnas_intradia"' in source
    assert '"columnas_grafico"' in source
    assert '"x_grafico_diaria"' in source
    assert '"x_grafico_intradia"' in source
    assert '"__nested_slot_map__"' in source


def test_option_base_ui_filters_24hs_liquidation() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "def ticker_es_liquidacion_24hs" in source
    assert "def ticker_liquidacion_ci_para_ui" in source
    assert "texto = ticker_liquidacion_ci_para_ui(ticker)" in source
    assert "if ticker_es_liquidacion_24hs(ticker):" in source
    assert "resultado = self._normalizar_opciones_selector_liquidacion(activas_hoy)" in source
    assert 'and not ticker_es_liquidacion_24hs(str(fila.get("ticker") or "").strip())' in source


def test_saved_option_expiration_is_restored_into_selector() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"vencimiento_general": self.var_vencimiento.get().strip()' in source
    assert '"mostrar_vencimientos_historicos": bool(self._mostrar_vencimientos_historicos.get())' in source
    assert "def _asegurar_vencimiento_en_selector" in source
    assert "self._asegurar_vencimiento_en_selector(vencimiento_general)" in source
    assert 'self.combo_vencimiento["values"] = self._vencimientos' in source


def test_expired_option_expirations_are_hidden_behind_toggle() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "self._vencimientos_todos" in source
    assert "self._mostrar_vencimientos_historicos = BooleanVar(value=False)" in source
    assert "def _vencimiento_es_historico" in source
    assert "fecha_venc < (ahora().date() - timedelta(days=7))" in source
    assert "def _toggle_vencimientos_historicos" in source
    assert 'textvariable=self.var_toggle_vencimientos_historicos' in source
    assert "def _vencimiento_seleccionable" in source


def test_saved_subview_bases_are_preserved_in_selector_options() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "def opciones_con_seleccion" in source
    assert "Conserva bases guardadas aunque todavia no aparezcan en la lista calculada" in source
    assert "opciones_slot = opciones_con_seleccion(opciones_generales, self._comp_vars_a[slot], self._comp_vars_b[slot])" in source
    assert "opciones_slot = opciones_con_seleccion(opciones_generales, self._tabla_rel_vars_a[slot], self._tabla_rel_vars_b[slot])" in source
    assert "opciones_backtest = opciones_con_seleccion(opciones_para_fecha(fecha_backtest), self._backtest_vars_a[slot], self._backtest_vars_b[slot])" in source


def test_expiration_state_persists_subviews_without_startup_overwrite() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"estado_vencimientos_ui": estado_vencimientos' in source
    assert '"estado_por_vencimiento": estado_vencimientos' in source
    assert '"subvistas_activas": int(self._subvistas_activas)' in source
    assert '"subvista_nombres": {str(slot): self._nombre_subvista(slot) for slot in self._comp_slots}' in source
    assert '"tabs_activas": {' in source
    assert "def _cargar_estado_vencimientos_ui_desde_payload" in source
    assert "def _normalizar_estado_vencimiento_ui" in source
    assert "self._subvistas_activas = self._resolver_subvistas_activas_guardadas(payload)" in source
    assert "_guardar_estado_slots_por_vencimiento" not in source
    assert "_aplicar_estado_slots_por_vencimiento" not in source


def test_relation_table_buttons_are_saved_per_expiration() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"tabla_relaciones": {' in source
    assert '"mostrar_ratio_mode": bool(self._tabla_rel_show_ratio_mode_vars[slot].get())' in source
    assert "def _aplicar_estado_visual_tabla_rel_slot" in source
    assert 'slots_tabla = ((data.get("tabla_relaciones") or {}).get("slots")' in source
    assert 'aplicar_bool("mostrar_ratio_mode"' in source
    assert "self._tabla_rel_show_ratio_mode_button_vars[slot].set" in source
    assert '"orden_columnas": list(self._tabla_rel_column_order_vars.get(slot, list(self.TABLA_REL_COLUMNAS)))' in source
    assert '"anchos_columnas_diaria": dict(self._tabla_rel_column_width_vars.get("diaria", {}).get(slot, {}))' in source


def test_state_persistence_uses_variable_traces_and_close_consolidation() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "def _registrar_trazas_persistencia_estado_ui" in source
    assert 'var.trace_add("write", self._al_traza_base_subvista)' in source
    assert "def _guardar_estado_vencimiento_actual" in source
    assert "def _restaurar_estado_vencimiento_ui" in source
    assert "def _consolidar_estado_ui_actual" in source
    assert "self._consolidar_estado_ui_actual()" in source
    assert "estado_vencimientos_ui" in source
    assert "self._cargar_estado_vencimientos_ui_desde_payload(payload)" in source


def test_manual_distribution_button_overrides_autosave_on_startup() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "self._ui_distribution_path = self.salida_dir / f\"ui_distribution_{self.subyacente.upper()}.json\"" in source
    assert 'text="Guardar distribución"' in source
    assert "command=self.guardar_distribucion_manual" in source
    assert "def guardar_distribucion_manual" in source
    assert "def _leer_payload_distribucion_manual" in source
    assert 'payload["distribucion_manual"] = True' in source
    assert "distribucion_manual = self._leer_payload_distribucion_manual()" in source
    assert "payload = distribucion_manual" in source


def test_manual_distribution_sanitizes_empty_slots_and_duplicate_names() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "def _limitar_subvistas_guardadas_por_config" in source
    assert "def _normalizar_nombres_subvistas_guardados" in source
    assert "return max(1, min(cantidad, ultimo_configurado or 1))" in source
    assert "if texto in usados:" in source
    assert 'texto = f"Vista {slot}"' in source
    assert "for tab_id in list(notebook.tabs()):" in source
    assert "notebook.forget(tab_id)" in source
    assert "notebook.add(tab, text=self._nombre_subvista(slot))" in source
    assert "def _slot_visible_desde_notebook" in source
    assert "def _seleccionar_tab_subvista_por_slot" in source
    assert "def _actualizar_selectores_subvista_hidratada" in source
    assert "self._actualizar_selectores_subvista_hidratada(notebook_attr)" in source
    assert "return self._limitar_subvistas_guardadas_por_config(data_venc, guardadas)" in source
    assert "if not permitir_defaults and (valor_a_slot or valor_b_slot):" in source


def test_startup_selector_refresh_does_not_overwrite_saved_subviews() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "self._estado_ui_cargado_desde_disco = False" in source
    assert "self._estado_ui_cargado_desde_disco = True" in source
    assert "self._normalizando_selectores_ui = False" in source
    assert "def set_normalizado" in source
    assert "protege_estado_guardado = bool(getattr(self, \"_estado_ui_cargado_desde_disco\", False)) and not bool(self._selector_values_cache)" in source
    assert "permitir_defaults=not protege_estado_guardado" in source
    assert "if hubo_cambio and not protege_estado_guardado:" in source
    assert "inicializar_todo=not bool(self._selector_values_cache)" not in source
    assert "inicializar_todo=False" in source


def test_drive_close_rebuild_button_and_incremental_import_exist() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'DRIVE_CIERRES_FOLDER_ID = "1HA_ZQ87eexmj4UXmq54ksWJDPwAxfVQo"' in source
    assert '"2026-06": "1qbL7YBKoe4ATAg4D3V5FsKYSpyNCAMUnWMfL7wALdyk"' in source
    assert 'text="Reconstruir cierres"' in source
    assert "command=self.reconstruir_cierres_desde_drive_async" in source
    assert "def _parsear_cierres_drive_csv" in source
    assert "def _reconstruir_cierres_desde_drive" in source
    assert "if self._history_db.obtener_tickers_cierre_fecha(fecha):" in source
    assert "omitidas_existentes += 1" in source
