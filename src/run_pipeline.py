"""GE2340 data/EDA + regression handoff.""" 
"""Nov 13 Update (Jeffrey): With classifier provided, but no neural network provided."""
from pathlib import Path
import argparse, hashlib, json, platform, os, tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "ge2340_matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "ge2340_cache"))
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score, balanced_accuracy_score, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
FEATURES=['Study_Hours_Per_Day','Extracurricular_Hours_Per_Day','Sleep_Hours_Per_Day','Social_Hours_Per_Day','Physical_Activity_Hours_Per_Day']
SHORT=['Study','Extracurricular','Sleep','Social','Physical activity']
TARGET='Grades'
SEED=2340

def dump(obj,path):
    Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')

def clean(raw):
    """Deterministic schema/domain checks; do not silently discard or impute rows."""
    needed=['Student_ID']+FEATURES+[TARGET]
    if not set(needed)<=set(raw):raise ValueError('Missing required columns')
    df=raw[needed].copy()
    for c in needed:df[c]=pd.to_numeric(df[c],errors='raise')
    if df.isna().any().any() or not np.isfinite(df.to_numpy()).all():raise ValueError('Missing/nonfinite values: review before proceeding')
    if df.Student_ID.duplicated().any():raise ValueError('Duplicate IDs: review before splitting')
    if (df.Student_ID%1!=0).any():raise ValueError('Noninteger IDs')
    if ((df[FEATURES]<0)|(df[FEATURES]>24)).any().any():raise ValueError('Time outside [0,24]')
    df.insert(0,'row_id',df.Student_ID.astype(int).map(lambda v:f'student_{v:04d}'))
    return df

def grade_labels(values,config):
    """User-approved cutpoints only. Intervals [lower,upper), final upper included."""
    if config.get('status')!='approved':raise ValueError('Grade bands pending approval')
    if config.get('target')!=TARGET:raise ValueError('Wrong target')
    cuts=np.asarray(config['cutpoints'],float)
    if len(cuts)!=4 or not np.isfinite(cuts).all() or np.any(np.diff(cuts)<=0):raise ValueError('Need four increasing finite cutpoints')
    labels=config.get('labels_low_to_high')
    if labels!=['F','D','C','B','A']:raise ValueError('Expected F,D,C,B,A order')
    if not config.get('rationale'):raise ValueError('Document grading rationale')
    return np.array(labels)[np.searchsorted(cuts,np.asarray(values),side='right')]

def write_grade_outputs(df,config,proc,out):
    proc=Path(proc);out=Path(out)
    if config.get("status")=="approved":
        labels=grade_labels(df[TARGET],config)
        labelled=df[["row_id","split",TARGET]].copy();labelled["grade_class"]=labels
        labelled.to_csv(proc/"grade_labels.csv",index=False)
        counts=pd.crosstab(labelled.grade_class,labelled.split).reindex(["F","D","C","B","A"],fill_value=0)
        counts.to_csv(out/"class_counts.csv")
        (proc/"classification_status.json").unlink(missing_ok=True)
        order=config['labels_low_to_high']
        train_counts=counts['train'].reindex(order)
        majority=str(train_counts.idxmax())  # deterministic F,D,C,B,A tie order
        rows=[]
        for split in ['train','validation','test']:
            d=labelled[labelled.split==split].copy()
            d['majority_prediction']=majority
            d.to_csv(out/f'classification_predictions_{split}.csv',index=False)
            y=d.grade_class;pred=d.majority_prediction
            rows.append({'split':split,'model':'train_majority_baseline','n':len(d),'accuracy':accuracy_score(y,pred),'macro_f1':f1_score(y,pred,labels=order,average='macro',zero_division=0),'balanced_accuracy':balanced_accuracy_score(y,pred)})
            pd.DataFrame(confusion_matrix(y,pred,labels=order),index=pd.Index(order,name='actual'),columns=order).to_csv(out/f'majority_confusion_{split}.csv')
        pd.DataFrame(rows).to_csv(out/'classification_metrics.csv',index=False)
        dump({'majority_class':majority,'fit_split':'train','train_class_counts':train_counts.to_dict(),'tie_rule':'first in F,D,C,B,A','cutpoints':config['cutpoints'],'test_examined':True,'no_test_tuning':True},out/'majority_baseline.json')
        dump(config,proc/'classification_contract.json')
        counts.div(counts.sum(axis=0),axis=1).to_csv(out/'class_proportions.csv')
        (out/'figures').mkdir(exist_ok=True)
        fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
        ax.bar(order,train_counts,color='#28698F')
        for i,n in enumerate(train_counts):ax.text(i,n+3,str(n),ha='center')
        ax.set(ylim=(0,max(train_counts)*1.15),xlabel='Project-defined relative group (not official grades)',ylabel='Training rows',title='Training-only grade groups (n=1,200)')
        savefig(fig,out/'figures/05_class_distribution_train')
    else:
        (proc/"grade_labels.csv").unlink(missing_ok=True)
        (out/"class_counts.csv").unlink(missing_ok=True)
        for name in ['classification_contract.json']:(proc/name).unlink(missing_ok=True)
        for pattern in ['class_proportions.csv','classification_metrics.csv','majority_baseline.json','classification_predictions_*.csv','majority_confusion_*.csv','figures/05_class_distribution_train.*']:
            for p in out.glob(pattern):p.unlink()
        dump({"status":"pending","reason":"Phase 1 gives A/B/C/D/F but no thresholds; no fabricated labels produced."},proc/"classification_status.json")

def make_splits(df):
    ids=np.arange(len(df))
    development,test=train_test_split(ids,test_size=.20,random_state=SEED,shuffle=True)
    train,validation=train_test_split(development,test_size=.25,random_state=SEED,shuffle=True)
    split=np.empty(len(df),dtype=object)
    for name,idx in [('train',train),('validation',validation),('test',test)]:split[idx]=name
    return split

def savefig(fig,path):
    fig.text(.01,-.025,'Source: Charlotte Bennett1234, Kaggle v3 | Data: ODbL / DbCL (see DATA_LICENSE.md)',fontsize=8,color='#555555')
    fig.savefig(str(path)+'.png',dpi=180,bbox_inches='tight')
    fig.savefig(str(path)+'.pdf',bbox_inches='tight')
    plt.close(fig)

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    figures=out/'figures';figures.mkdir(exist_ok=True)
    raw_path=ROOT/'data/raw/student_lifestyle_dataset..csv'
    raw=pd.read_csv(raw_path);df=clean(raw);df['split']=make_splits(df)
    proc=out/'processed';proc.mkdir(exist_ok=True)
    df.to_csv(proc/'clean_data_with_splits.csv',index=False)
    df[['row_id','Student_ID','split']].to_csv(proc/'split_manifest.csv',index=False)
    sets={s:df[df.split==s].copy() for s in ['train','validation','test']}
    train=sets['train'];scaler=StandardScaler().fit(train[FEATURES])
    dump({'features':FEATURES,'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),'fit_split':'train','fit_row_ids':train.row_id.tolist()},proc/'preprocessor.json')
    for s,d in sets.items():
        d[['row_id']+FEATURES+[TARGET]].to_csv(proc/f'{s}_raw.csv',index=False)
        scaled=pd.DataFrame(scaler.transform(d[FEATURES]),columns=FEATURES)
        scaled.insert(0,'row_id',d.row_id.to_numpy());scaled[TARGET]=d[TARGET].to_numpy()
        scaled.to_csv(proc/f'{s}_scaled.csv',index=False)
    # Five time features sum to 24 in this source. Drop physical activity only for
    # the linear model, using it as the reference activity; export all five for Jeffrey.
    if not np.allclose(train[FEATURES].sum(axis=1),24,atol=1e-9):
        raise ValueError("Fixed-sum assumption changed; review OLS reference parameterization")
    lr_features=FEATURES[:-1]
    model=LinearRegression().fit(train[lr_features],train[TARGET])
    mean=float(train[TARGET].mean());metrics=[]
    for s,d in sets.items():
        pred=model.predict(d[lr_features]);base=np.repeat(mean,len(d))
        pd.DataFrame({'row_id':d.row_id,'observed_Grades':d[TARGET],'linear_regression':pred,'mean_baseline':base}).to_csv(out/f'predictions_{s}.csv',index=False)
        for name,p in [('linear_regression',pred),('mean_baseline',base)]:
            metrics.append({'split':s,'model':name,'n':len(d),'MAE':mean_absolute_error(d[TARGET],p),'RMSE':np.sqrt(mean_squared_error(d[TARGET],p)),'R2':r2_score(d[TARGET],p)})
    pd.DataFrame(metrics).to_csv(out/'metrics.csv',index=False)
    dump({'estimator':'sklearn.linear_model.LinearRegression','loss':'squared_error','provisional_phase1_change':False,'phase1_loss_verified':'MSE; user-uploaded submitted Phase1_Proposal.pdf, page 1','features':lr_features,'reference_feature':FEATURES[-1],'intercept':float(model.intercept_),'coefficients':model.coef_.tolist(),'mean_baseline':mean,'fit_split':'train','no_clipping':True},out/'regression_model.json')
    sums=df[FEATURES].sum(axis=1)
    audit={'raw_rows':len(raw),'clean_rows':len(df),'raw_columns':raw.columns.tolist(),'excluded_features':['Student_ID','Stress_Level','Gender'],'null_counts':raw.isna().sum().to_dict(),'exact_duplicate_rows':int(raw.duplicated().sum()),'duplicate_student_ids':int(raw.Student_ID.duplicated().sum()),'rows_removed':0,'rows_imputed':0,'hours_sum_min':float(sums.min()),'hours_sum_max':float(sums.max()),'all_hours_sum_24':bool(np.allclose(sums,24,atol=1e-9)),'centered_train_feature_rank':int(np.linalg.matrix_rank(train[FEATURES]-train[FEATURES].mean())),'observed_Grades_min':float(df[TARGET].min()),'observed_Grades_max':float(df[TARGET].max()),'theoretical_grade_scale':'unverified; keep original values','split_counts':df.split.value_counts().to_dict(),'seed':SEED,'raw_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),'classification':json.loads((ROOT/'config/grade_bands.json').read_text())['status']}
    dump(audit,out/'quality_audit.json')
    train[FEATURES+[TARGET]].describe().to_csv(out/'train_descriptive_statistics.csv')
    corr=train[FEATURES+[TARGET]].corr();corr.to_csv(out/'train_correlations.csv')
    # Training-only outlier flags are descriptive, not deletion rules.
    q1=train[FEATURES+[TARGET]].quantile(.25);q3=train[FEATURES+[TARGET]].quantile(.75)
    iqr=q3-q1;flags=((train[FEATURES+[TARGET]]<q1-1.5*iqr)|(train[FEATURES+[TARGET]]>q3+1.5*iqr)).sum()
    flags.rename('training_IQR_flags_not_removed').to_csv(out/'train_outlier_flags.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold'})
    fig,axs=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for ax,col,title in zip(axs.flat,FEATURES+[TARGET],SHORT+['Grades (original units)']):
        ax.hist(train[col],bins=18,color='#28698F',edgecolor='white',linewidth=.4);ax.set_title(title);ax.set_ylabel('Students');ax.set_xlabel('Hours/day' if col in FEATURES else 'Grades')
    fig.suptitle(f'Training-set distributions (n={len(train)})',fontsize=15);savefig(fig,figures/'01_distributions_train')
    fig,ax=plt.subplots(figsize=(8,7),layout='constrained');im=ax.imshow(corr,vmin=-1,vmax=1,cmap='PuOr_r')
    ax.set_xticks(range(6),SHORT+['Grades'],rotation=40,ha='right');ax.set_yticks(range(6),SHORT+['Grades'])
    for i in range(6):
        for j in range(6):ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',color='white' if abs(corr.iloc[i,j])>.65 else '#1f2937')
    fig.colorbar(im,ax=ax,label='Pearson correlation');ax.set_title('Training-set correlations (association, not causation)');savefig(fig,figures/'02_correlations_train')
    fig,axs=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for ax,col,title in zip(axs.flat,FEATURES,SHORT):
        ax.scatter(train[col],train[TARGET],s=9,alpha=.35,color='#28698F',rasterized=True);ax.set_title(title);ax.set_xlabel('Hours/day');ax.set_ylabel('Grades (original units)')
    axs.flat[-1].axis('off');fig.suptitle('Time use and Grades — training data only',fontsize=15);savefig(fig,figures/'03_relationships_train')
    # Validation diagnostic, explicitly not EDA on held-out test.
    v=sets['validation'];pred=model.predict(v[lr_features]);fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    axs[0].scatter(v[TARGET],pred,s=14,alpha=.5,color='#28698F');lo=min(v[TARGET].min(),pred.min());hi=max(v[TARGET].max(),pred.max());axs[0].plot([lo,hi],[lo,hi],'--',color='#333333');axs[0].set(xlabel='Observed Grades',ylabel='Predicted Grades',title='Validation predictions')
    axs[1].scatter(pred,v[TARGET]-pred,s=14,alpha=.5,color='#28698F');axs[1].axhline(0,color='#333333',ls='--');axs[1].set(xlabel='Predicted Grades',ylabel='Observed − predicted',title='Validation residuals');savefig(fig,figures/'04_validation_diagnostics')
    config=json.loads((ROOT/'config/grade_bands.json').read_text())
    write_grade_outputs(df,config,proc,out)

    # After finishing the regression model, we proceed to the classifier model.
    run_classifier(out, proc, sets);

    dump({'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scikit_learn':sklearn.__version__,'matplotlib':matplotlib.__version__},out/'environment.json')
    print(pd.DataFrame(metrics).to_string(index=False));print(json.dumps(audit,indent=2))

from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

def run_classifier(out, proc, sets):
    out = Path(out)
    figures = out / 'figures'
    figures.mkdir(exist_ok=True)

    grades_path = proc / 'grade_labels.csv'
    if not grades_path.exists():
        print("Grade labels not approved/available; skipping classifier.")
        return

    grades_df = pd.read_csv(grades_path)
    order = ['F', 'D', 'C', 'B', 'A']
    
    # Merge train scaled with grade labels
    train_merged = sets['train'].merge(grades_df[['row_id', 'grade_class']], on='row_id')
    X_train = train_merged[FEATURES] # SGD handles all 5 features natively
    y_train = train_merged['grade_class']

    # Initialize and train SGD classifier with cross-entropy loss
    # Build a pipeline that expands features, scales them, then runs the SGD classifier
    pipeline = Pipeline([
        ('poly', PolynomialFeatures(degree=2, include_bias=False)),
        ('scaler', StandardScaler()),
        ('clf', SGDClassifier(
            loss='log_loss', 
            penalty='elasticnet',  
            l1_ratio=0.15,         
            alpha=0.001,           
            learning_rate='constant',
            eta0=0.005,            
            class_weight={
                'F': 1.0,
                'D': 1.3,     
                'C': 1.4,
                'B': 1.4, 
                'A': 0.9
            },
            max_iter=3000, 
            random_state=SEED
        ))
    ])
    pipeline.fit(X_train, y_train)

    # Output file formats.
    fig_meta = {
        'train': ('06_sgd_confusion_train', 'SGD Classifier Confusion Matrix — Training Set'),
        'validation': ('07_sgd_confusion_validation', 'SGD Classifier Confusion Matrix — Validation Set'),
        'test': ('08_sgd_confusion_test', 'SGD Classifier Confusion Matrix — Test Set')
    }

    class_metrics = []
    for s, d in sets.items():
        d_merged = d.merge(grades_df[['row_id', 'grade_class']], on='row_id')
        X_split = d_merged[FEATURES]
        y_true = d_merged['grade_class']
        
        y_pred = pipeline.predict(X_split)
        
        acc = accuracy_score(y_true, y_pred)
        macro_f1 = f1_score(y_true, y_pred, labels=order, average='macro', zero_division=0)
        bal_acc = balanced_accuracy_score(y_true, y_pred)
        
        class_metrics.append({
            'split': s,
            'model': 'sgd_crossentropy_classifier',
            'n': len(d_merged),
            'accuracy': acc,
            'macro_f1': macro_f1,
            'balanced_accuracy': bal_acc
        })
        
        # Save confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=order)
        pd.DataFrame(cm, index=pd.Index(order, name='actual'), columns=order).to_csv(
            out / f'sgd_confusion_{s}.csv'
        )

        # Generate and save visual heatmap (both PNG and PDF via savefig)
        fig_name, fig_title = fig_meta[s]
        fig, ax = plt.subplots(figsize=(6.5, 5.5), layout='constrained')
        im = ax.imshow(cm, cmap='Blues', vmin=0)
        
        ax.set_xticks(range(len(order)), order)
        ax.set_yticks(range(len(order)), order)
        ax.set_xlabel('Predicted Grade')
        ax.set_ylabel('Actual Grade')
        ax.set_title(f"{fig_title} (n={len(d_merged)})")
        
        # Annotate cells with exact student counts, adjusting text contrast dynamically
        thresh = cm.max() / 2.0
        for i in range(len(order)):
            for j in range(len(order)):
                ax.text(
                    j, i, f'{cm[i, j]}',
                    ha='center', va='center',
                    color='white' if cm[i, j] > thresh else '#1f2937',
                    fontweight='bold' if i == j else 'normal'
                )
                
        fig.colorbar(im, ax=ax, label='Student Count')
        savefig(fig, figures / fig_name)

    pd.DataFrame(class_metrics).to_csv(out / 'sgd_classification_metrics.csv', index=False)
    print("SGD Classifier evaluation complete and metrics saved.")

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=ROOT/'outputs')
    a=p.parse_args()
    run(a.out)
