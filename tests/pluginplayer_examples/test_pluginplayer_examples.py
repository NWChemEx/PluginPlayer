import pluginplayer_examples as ppe
import pluginplay as pp


mm = pp.ModuleManager()
ppe.load_modules(mm)
print(mm.keys())