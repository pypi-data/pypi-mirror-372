# relcheck
A CLI tool to check diagnose reliability of kubernetes resources


## Minikube setup
`minikube dashboard`
kubectl expose deployment myapp --type=NodePort --port=8080
minikube service myapp
`minikube stop`

### Initial Plan
can u design the flow diagram for this service i planned
Okay here is the full plan
We will create this CLI tool called relcheck here
It will diagnose problems with kubernetes resources

I want u to create a structure so that we can code,
i want a base class called Resource which will have general information about the resource for example pod
then this class will also load something called checks
a check corresponds to a check of certain kind say for example checking for missing resource limits in a pod or checking for anything, i want u to create a base check class as well so that users can code their own checks
Now when we run the Resource class wil load the checks and run it against the resource for example pod info stored in the Resource class object, 
It should output something called a ReportInfo
the ReportInfo is a list of information mainly contain the check that was performed, did it pass or fail, some information on why the check passed or failed and also contains an empty solution string u can say i dont want the solution populated right now as we will connect a MCP provide it the report and ask the MCP to provide solutions
Now all the list of ReportInfo that come from various Resource classes which inside them perform checks and create the ReportInfo object will then be combined into a final Report class which can further be exported to json, table etc

Now a few things, i want the checks to be seperated based on resource types example pod etc in kubernetes and i want them to follow the same Check base class

Also in the Report Class i want an option to invoke MCP based solutioning so u can implement something seperately than can be invoked to call a MCP LLM Model and populate the solutions field of the report

in the MCP layer i also want that before we send the request we can provide additional context related to the Resource

can u implement all this in a minimal fashion


### Kubernetes Resources
Cluster
 ├── Namespaces (default, kube-system, etc.)
 │    ├── Workloads
 │    │    ├── Pods
 │    │    ├── Deployments (manages ReplicaSets -> Pods)
 │    │    ├── StatefulSets (manages Pods with identity & PVCs)
 │    │    └── DaemonSets (ensures Pods on all Nodes)
 │    │
 │    ├── Networking
 │    │    ├── Services (target Pods via labels)
 │    │    ├── Ingress (routes external traffic → Services)
 │    │    └── NetworkPolicy (controls Pod traffic)
 │    │
 │    ├── Data
 │    │    ├── ConfigMaps (key-value data for Pods)
 │    │    ├── Secrets (sensitive data for Pods)
 │    │    └── PersistentVolumeClaims (PVCs → bind to PVs)
 │    │
 │    └── RBAC (Roles, RoleBindings scoped to this namespace)
 │
 ├── Nodes (where Pods actually run, scheduled by kube-scheduler)
 │    └── Each Node runs kubelet + container runtime
 │
 └── Cluster-scoped configs
      ├── PersistentVolumes (PV) – available across namespaces
      ├── ClusterRoles / ClusterRoleBindings
      └── CRDs (define new resource types)

