import sys, json, unittest, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from run_pipeline import ROOT, FEATURES, TARGET, clean, grade_labels, make_splits, write_grade_outputs
class Checks(unittest.TestCase):
 def setUp(self):
  self.raw=pd.read_csv(ROOT/'data/raw/student_lifestyle_dataset..csv');self.df=clean(self.raw)
  self.out=ROOT/'outputs';self.p=self.out/'processed'
 def test_clean_preserves(self):
  self.assertEqual(len(self.df),2000);self.assertFalse(self.df.isna().any().any())
  np.testing.assert_array_equal(self.df[TARGET],self.raw[TARGET])
 def test_manifest(self):
  m=pd.read_csv(self.p/'split_manifest.csv');self.assertTrue(m.row_id.is_unique)
  self.assertEqual(m.split.value_counts().to_dict(),{'train':1200,'test':400,'validation':400})
  np.testing.assert_array_equal(m.split,make_splits(self.df))
  sets=[set(m.loc[m.split==s,'row_id']) for s in ['train','validation','test']]
  for i in range(3):
   for j in range(i):self.assertFalse(sets[i]&sets[j])
 def test_scaler_train_only(self):
  tr=pd.read_csv(self.p/'train_raw.csv');params=json.loads((self.p/'preprocessor.json').read_text())
  np.testing.assert_allclose(params['mean'],tr[FEATURES].mean(),rtol=1e-12)
  np.testing.assert_allclose(params['scale'],tr[FEATURES].std(ddof=0),rtol=1e-12)
  self.assertEqual(set(params['fit_row_ids']),set(tr.row_id))
  for s in ['train','validation','test']:
   r=pd.read_csv(self.p/f'{s}_raw.csv');z=pd.read_csv(self.p/f'{s}_scaled.csv')
   np.testing.assert_array_equal(r.row_id,z.row_id)
   np.testing.assert_allclose(z[FEATURES],(r[FEATURES]-params['mean'])/params['scale'],atol=1e-12)
 def test_baseline_train_only(self):
  tr=pd.read_csv(self.p/'train_raw.csv');model=json.loads((self.out/'regression_model.json').read_text())
  self.assertAlmostEqual(model['mean_baseline'],tr[TARGET].mean())
  for s in ['train','validation','test']:
   p=pd.read_csv(self.out/f'predictions_{s}.csv');np.testing.assert_allclose(p.mean_baseline,tr[TARGET].mean())
 def test_metrics_recompute(self):
  from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
  m=pd.read_csv(self.out/'metrics.csv')
  for _,row in m.iterrows():
   p=pd.read_csv(self.out/f'predictions_{row.split}.csv');y=p.observed_Grades;pred=p[row.model]
   self.assertAlmostEqual(row.MAE,mean_absolute_error(y,pred));self.assertAlmostEqual(row.RMSE,np.sqrt(mean_squared_error(y,pred)));self.assertAlmostEqual(row.R2,r2_score(y,pred))
 def test_approved_labels_and_quintiles(self):
  c=json.loads((ROOT/'config/grade_bands.json').read_text())
  tr=pd.read_csv(self.p/'train_raw.csv')
  np.testing.assert_allclose(tr.Grades.quantile([.2,.4,.6,.8]),c['cutpoints'])
  labels=pd.read_csv(self.p/'grade_labels.csv')
  self.assertEqual(len(labels),2000);self.assertTrue(labels.row_id.is_unique)
  np.testing.assert_array_equal(labels.grade_class,grade_labels(labels.Grades,c))
  self.assertEqual(labels[labels.split=='train'].grade_class.value_counts().to_dict(),{'B':249,'A':243,'F':238,'D':236,'C':234})
  np.testing.assert_array_equal(grade_labels([7.099,7.1,7.55,8,8.45],c),['F','D','C','B','A'])
  with self.assertRaises(ValueError):grade_labels([7],{'status':'pending'})
 def test_majority_recompute(self):
  from sklearn.metrics import accuracy_score,f1_score,balanced_accuracy_score
  model=json.loads((self.out/'majority_baseline.json').read_text());self.assertEqual(model['majority_class'],'B')
  m=pd.read_csv(self.out/'classification_metrics.csv')
  for _,v in m.iterrows():
   p=pd.read_csv(self.out/f'classification_predictions_{v.split}.csv');self.assertTrue((p.majority_prediction=='B').all())
   self.assertAlmostEqual(v.accuracy,accuracy_score(p.grade_class,p.majority_prediction))
   self.assertAlmostEqual(v.macro_f1,f1_score(p.grade_class,p.majority_prediction,labels=['F','D','C','B','A'],average='macro',zero_division=0))
   self.assertAlmostEqual(v.balanced_accuracy,balanced_accuracy_score(p.grade_class,p.majority_prediction))
 def test_label_boundary_function(self):
  c={'status':'approved','target':'Grades','cutpoints':[1,2,3,4],'labels_low_to_high':['F','D','C','B','A'],'rationale':'unit-test only, NOT project thresholds'}
  np.testing.assert_array_equal(grade_labels([.9,1,2,3,4,5],c),['F','D','C','B','A','A'])
 def test_label_output_transitions(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);proc=out/'processed';proc.mkdir()
   d=self.df.copy();d['split']=make_splits(d)
   c={'status':'approved','target':'Grades','cutpoints':[1,2,3,4],'labels_low_to_high':['F','D','C','B','A'],'rationale':'test fixtures only, not project labels'}
   write_grade_outputs(d,{'status':'pending'},proc,out)
   self.assertTrue((proc/'classification_status.json').exists())
   write_grade_outputs(d,c,proc,out)
   self.assertTrue((proc/'grade_labels.csv').exists());self.assertFalse((proc/'classification_status.json').exists())
   write_grade_outputs(d,{'status':'pending'},proc,out)
   self.assertFalse((proc/'grade_labels.csv').exists());self.assertFalse((out/'class_counts.csv').exists());self.assertTrue((proc/'classification_status.json').exists())
 def test_fixed_sum_and_reference(self):
  np.testing.assert_allclose(self.df[FEATURES].sum(axis=1),24)
  model=json.loads((self.out/'regression_model.json').read_text());self.assertEqual(model['features'],FEATURES[:-1])
 def test_bad_input_fails(self):
  x=self.raw.copy();x.loc[0,FEATURES[0]]=np.nan
  with self.assertRaises(ValueError):clean(x)
  x=self.raw.copy();x.loc[0,FEATURES[0]]=-1
  with self.assertRaises(ValueError):clean(x)
if __name__=='__main__':unittest.main()
