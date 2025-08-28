from sklearn.cluster import KMeans, AgglomerativeClustering, HDBSCAN
#----------------------------------------------------------------------------------------------------------

def clustering_agg(lista, descriptors, n_clusters):

    if len(descriptors) < n_clusters:
        print("La cantidad de descriptores es menor que el número de clusters. Devolviendo la lista original.")
        return {0: lista}
    else:
        model = AgglomerativeClustering(n_clusters=n_clusters)
        labels = model.fit_predict(descriptors)
        
    clusters = {i: [] for i in range(n_clusters)}
    for idx, label in enumerate(labels):
        clusters[label].append(lista[idx])
    
    return clusters
#-----------------------------------------------------------------------------------------------------------

def clustering_kmeans (lista, descriptors, n_clusters):
    
    if len(descriptors) < n_clusters:
        print("La cantidad de descriptores es menor que el número de clusters. Devolviendo la lista original.")
        return {0: lista}
    else:
        model = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=3000, tol=1e-7)
        model.fit(descriptors)
        labels = model.labels_
        
    clusters = {i: [] for i in range(n_clusters)}
    for idx, label in enumerate(labels):
        clusters[label].append(lista[idx])

    return clusters
#--------------------------------------------------------------------------------------------------------------
    
def clustering_hdbscan(lista, descriptores):
    if len(descriptores) < 100:
        print("La cantidad de descriptores es menor a 100. Devolviendo la lista original.")
        return {0: lista}
    
    model = HDBSCAN(min_cluster_size = 5, cluster_selection_epsilon = 0.2, cluster_selection_method = "eom")
    #model = DBSCAN()
    model.fit(descriptores)

    labels = model.labels_
    n_clus = len(set(labels))

    clusters = {label: [] for label in set(labels)}  

    for idx, label in enumerate(labels):
        clusters[label].append(lista[idx])

    return clusters, n_clus
