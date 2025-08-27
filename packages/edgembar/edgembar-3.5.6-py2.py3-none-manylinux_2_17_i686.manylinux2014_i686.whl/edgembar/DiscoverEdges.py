#!/usr/bin/env python3
from typing import List
from . Edge import Edge


def string_to_dict(string, pattern):
    import re
    # https://stackoverflow.com/a/36838374
    regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', pattern)
    values = list(re.search(regex, string).groups())
    keys = re.findall(r'{(.+?)}', pattern)
    _dict = dict(zip(keys, values))
    return _dict


#fmt = r"dats/{trial}/free_energy/{edge}_ambest/{env}/{stage}/efep_{traj}_{ene}.dat"



def DiscoverEdges(fmt: str, exclude_trials=None,target=None,reference=None) -> List[Edge]:
    from . Trial import Trial
    from . Stage import Stage
    from . Env   import Env
    from . Edge  import Edge
    from glob    import glob
    from pathlib import Path
    from collections import defaultdict as ddict

    keys = {}
    for placeholder in ["trial","edge","env","stage","traj","ene"]:
        if "{%s}"%(placeholder) in fmt:
            keys[placeholder] = "*"
    
    #globstr = fmt.format(trial="*",edge="*",env="*",stage="*",traj="*",ene="*")
    globstr = fmt.format(**keys)

    dats = [ Path(x) for x in sorted(glob(globstr)) ]

    valid_complexs = ["target","tgt"]
    valid_solvated = ["reference","ref"]
    if target is not None:
        valid_complexs = [ target ]
    if reference is not None:
        valid_solvated = [ reference ]
    ntarget = 0
    nreference = 0
    com_name = valid_complexs[0]
    sol_name = valid_solvated[0]
    
    edges = ddict( lambda: ddict( lambda: ddict( lambda: ddict(list) ) ) )
    for dat in dats:
        m = string_to_dict(str(dat),fmt)
        if "trial" in m:
            trial = m["trial"]
        else:
            trial = "1"
        if exclude_trials is not None:
            if trial in exclude_trials:
                continue
            
        if "edge" in m:
            edge  = m["edge"]
        else:
            raise Exception("The discovery string must contain '{edge}'")
        if "env" in m:
            env   = m["env"]
            if env not in valid_complexs and env not in valid_solvated:
                continue
                #raise Exception(("{edge} can only be "
                #                 f"{valid_complexs} or {valid_solvated} "
                #                 f"but found {env} in {dat}"))
            if env in valid_complexs:
                com_name = env
                env = "target"
                ntarget += 1
            elif env in valid_solvated:
                sol_name = env
                env = "reference"
                nreference += 1
        else:
            env = "target"
        if "stage" in m:
            stage = m["stage"]
        else:
            stage = "STAGE"
        if "ene" in m:
            ene   = m["ene"]
        else:
            raise Exception("The discovery string must contain '{ene}'")
        if ene not in edges[edge][env][stage][trial]:
            edges[edge][env][stage][trial].append(ene)


    if target is not None:
        if ntarget == 0:
            raise Exception(f"target name manually set to '{target}',"
                            f" but no directories had that name")
    if reference is not None:
        if nreference == 0:
            raise Exception(f"reference name manually set to '{reference}',"
                            f" but no directories had that name")

    if len(edges) == 0:
        raise Exception("No edges were found")
        
    edgeobjs = []
    for edge in edges:
        envs = []
        for env in edges[edge]:
            env_name = None
            if env == "target":
                env_name = com_name
            elif env == "reference":
                env_name = sol_name
            stages = []
            for stage in edges[edge][env]:
                trials = []
                for trial in edges[edge][env][stage]:
                    ene = edges[edge][env][stage][trial]
                    datadir = Path(fmt.format(trial=trial,edge=edge,env=env_name,stage=stage,traj="TRAJ",ene="ENE")).parent
                    if not datadir.is_dir():
                        raise Exception("Directory not found %s"%(datadir))
                    datadir = "%s"%(str(datadir))
                    ene.sort()
                    trials.append(Trial(trial,datadir,ene))
                stages.append(Stage(stage,trials))
            envs.append(Env(env,stages))
        envnames = [env.name for env in envs]
        cmpl = None
        if "target" in envnames:
            cmpl = envs[envnames.index("target")]
        solv = None
        if "reference" in envnames:
            solv = envs[envnames.index("reference")]
        edgeobjs.append(Edge(edge,cmpl,solv))
    return edgeobjs

