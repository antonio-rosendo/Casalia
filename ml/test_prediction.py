from backend_features import build_features_for_request, run_prediction
import pprint

print("--- RAW FEATURES PASSED TO THE MODEL ---")
features = build_features_for_request(comunidad_autonoma="madrid", precio_total=250000, metros_cuadrados=80)
pprint.pprint(features)
print("\n--- INFERENCE RESULT ---")
result = run_prediction(comunidad_autonoma="madrid", precio_total=250000, metros_cuadrados=80)
print(result)
