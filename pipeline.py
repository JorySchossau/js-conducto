"""
### **Demo CI/CD Pipeline**
This is my example pipeline using Conducto:

It performs an experiment of evolving reinforcement-learning
agents (AutoML) in either a static environment, vs a changing
environment, then plots the mean and 95% conf interval of fitness.
The static environment should yield the fastest fitness gains
early in evolution, but be hindered by historical contingency
later in evolutionary time, outperformed by the population
that experienced a more dynamic environment. (unpublished)
"""

import conducto as co
import configparser
import os

experiment_command = """
./code/mabe -p GLOBAL-updates 100 BRAIN-brainType TDLambda WORLD_CONVEYORBELT-numThreads 1 WORLD_CONVEYORBELT-trials 2 WORLD_CONVEYORBELT-trialLength 20 BRAIN_TDLAMBDA-useConfidence 0 BRAIN_TDLAMBDA-pRandomAction 0.01 GENOME_CIRCULAR-sizeInitial 36 GENOME_CIRCULAR-sizeMax 36 GENOME_CIRCULAR-sizeMin 36 GENOME-sitesType double GENOME-alphabetSize 1000 GENOME_CIRCULAR-mutationPointOffsetRange 1.0 GENOME_CIRCULAR-mutationPointOffsetRate 0.01 GENOME_CIRCULAR-mutationPointRate 0.01 GENOME_CIRCULAR-mutationPointOffsetUniform 0 WORLD_CONVEYORBELT-logActions 0 WORLD_CONVEYORBELT-logRewards 0 WORLD_CONVEYORBELT-logSensors 0 ARCHIVIST_LODWAP-dataSequence :1 ARCHIVIST_LODWAP-organismsSequence :1 ARCHIVIST_LODWAP-writeDataFile 1 ARCHIVIST_LODWAP-writeOrganismsFile 1 ARCHIVIST_LODWAP-terminateAfter 0"""

def save_data(rep_i:int):
    result_path = f"rep{rep_i}p1"
    co.data.pipeline.put(result_path, "LOD_data.csv")

def parallelize_reps(reps:int) -> co.Parallel:
    output = co.Parallel()
    data_size = reps
    min_rep = 0
    max_rep = reps

    for rep_i in range(min_rep,max_rep):
        print("inside rep " + str(rep_i))
        output[f'rep{rep_i}'] = co.Serial()
        # unpredictable
        output[f'rep{rep_i}']['p1'] = co.Exec(f"{experiment_command} GLOBAL-randomSeed {rep_i} WORLD_CONVEYORBELT-randomize 1 && conducto-perm-data put --name rep{rep_i}p1 --file LOD_data.csv")
        # predictable
        output[f'rep{rep_i}']['p0'] = co.Exec(f"{experiment_command} GLOBAL-randomSeed {rep_i} WORLD_CONVEYORBELT-randomize 0 && conducto-perm-data put --name rep{rep_i}p0 --file LOD_data.csv")
    return output

def plot_reps(reps:int):
    min_rep = 0
    max_rep = reps
    os.makedirs("predictable", exist_ok=True)
    os.makedirs("unpredictable", exist_ok=True)
    for rep_i in range(min_rep,max_rep):
        p0 = os.path.join("predictable",str(rep_i))
        p1 = os.path.join("unpredictable",str(rep_i))
        os.makedirs(p0, exist_ok=True)
        os.makedirs(p1, exist_ok=True)
        co.perm_data.get(f"rep{rep_i}p0", os.path.join(p0,"LOD_data.csv"))
        co.perm_data.get(f"rep{rep_i}p1", os.path.join(p1,"LOD_data.csv"))
    os.system('python code/quickview.py')
    co.perm_data.put("summary_results","figure.png")
    print(f"""
<ConductoMarkdown>

### **Demo CI/CD Pipeline**

This is my example pipeline using Conducto:

It performs an experiment of evolving reinforcement-learning
agents (AutoML) in either a static environment, vs a changing
environment, then plots the mean and 95% conf interval of fitness.
The static environment should yield the fastest fitness gains
early in evolution, but be hindered by historical contingency
later in evolutionary time, outperformed by the population
that experienced a more dynamic environment. (unpublished)

![img]({co.perm_data.url("summary_results")} "Summary Results")
</ConductoMarkdown>
""")

def run() -> co.Serial:
    cfg = configparser.ConfigParser()
    cfg.read('config.ini'); # work config params (reps)
    reps = cfg['params']['replicates']
    print(f'running with {reps} replicates')
    image = co.Image(image="gbly/miniconda3", copy_dir=".", reqs_py=['conducto==0.0.67'])
    with co.Serial(image=image, doc=co.util.magic_doc()) as pipeline:
        #pipeline["python_trial"] = co.Exec("python -c 'import pandas as pd'")
        pipeline["parallel_experiment"] = co.Lazy(parallelize_reps, reps=int(reps))
        pipeline["plot_data"] = co.Exec(plot_reps, reps=int(reps))
    return pipeline

if __name__ == "__main__":
    print(__doc__)
    co.main(default=run)
    #url = 'figure.pdf'
    #markdown = f"""
    #<ConductoMarkdown>
    #![plot]({url} "Evolution...")
    #</ConductoMarkdown>
    #"""
    #print(markdown)
