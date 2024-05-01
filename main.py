import glob

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load all the csv files from the Datos folder as separate dataframes
# we will use a glob to get all the files in the folder
# and then we will use a dictionary comprehension to load all the files as dataframes

path_glob = "./Datos/*.csv"

dataframes = {file: pd.read_csv(file) for file in glob.glob(path_glob)}

# Combine all the dataframes into a single dataframe
combined_df = pd.concat(dataframes.values(), ignore_index=True)

# There are some negative values that are incorrect because the values should be positive
# but the issue is only in the sign, the data itself is correct

# We use the abs method to convert all the values to positive only on the columns that are numeric
numeric_columns = combined_df.select_dtypes(include=[int, float]).columns
combined_df[numeric_columns] = combined_df[numeric_columns].abs()

df = combined_df

# We make sure that the type is correct (just in case)
df['grupo'] = df['grupo'].astype('category')
df['alumno'] = df['alumno'].astype('category')

# Each student has made 2 attempts so we will group by the 'alumno' and 'grupo' columns and calculate the mean
df = df.groupby(['alumno', 'grupo']).mean().reset_index()
# Clean up all the rows with NaN values generated by the groupby operation
df = df.dropna().reset_index(drop=True)

# We use the median to fill the missing values to avoid the outliers but only for the numeric columns
# We group by the 'grupo' column and apply the median to each group
# We use the transform method to apply the median to the missing values
# We use the fillna method to fill the missing values with the calculated medians

medians = df.groupby('grupo')[numeric_columns].transform(lambda x: x.fillna(x.median()))

# We update the dataframe with the new values
df[numeric_columns] = df[numeric_columns].fillna(medians)

# Now that we have the data cleaned we can proceed to apply the PCA
# We first need to separate the numeric columns
numerical_data = df[numeric_columns]

# We then need to normalize the data using the StandardScaler
scaler = StandardScaler()
normalized_data = scaler.fit_transform(numerical_data)

# We instantiate the PCA object and specify the number of components we want to calculate
# We can specify the number of components we want to calculate but we will use None to get all the components
pca = PCA(n_components=None)
main_components = pca.fit_transform(normalized_data)

# We can get the eigenvectors (main components) and eigenvalues (explained variance) from
# the pca object using the components_ and explained_variance_ attributes
eigenvectors = pca.components_
eigenvalues = pca.explained_variance_

# Print the data
logger.info("Autovectores (Componentes Principales):")
logger.info(eigenvectors)
logger.info("\nAutovalores (Varianza explicada por cada componente):")
logger.info(eigenvalues)

# We can also get the explained variance ratio which is the percentage of variance explained by each component
explained_variance = pca.explained_variance_ratio_
logger.info("\nVarianza explicada por cada componente principal:")
logger.info(explained_variance)

# Lastly, we can get the cumulative explained variance ratio which is the cumulative sum of the explained variance ratio
logger.info("\nVarianza explicada acumulada:")
logger.info(explained_variance.cumsum())

plt.figure(figsize=(8, 4))
plt.plot(eigenvalues, 'o-')
plt.title('Scree Plot')
plt.xlabel('Número de Componentes')
plt.ylabel('Autovalores')
plt.grid(True)
plt.show()

# The scree plot shows the eigenvalues of the principal components and it is used to determine the number of components to keep
# We can see that the first two components explain more variance and the rest of the components explain less variance
# This is known as the elbow method and it is used to determine the number of components to keep

# We reduce the number of components to 2
pca = PCA(n_components=2)
main_components = pca.fit_transform(normalized_data)
eigenvectors = pca.components_
eigenvalues = pca.explained_variance_

# We can also get the explained variance ratio which is the percentage of variance explained by each component
explained_variance = pca.explained_variance_ratio_
logger.info("Varianza explicada por cada componente principal:")
logger.info(explained_variance)

# Lastly, we can get the cumulative explained variance ratio which is the cumulative sum of the explained variance ratio
logger.info("Varianza explicada acumulada:")
logger.info(explained_variance.cumsum())

# We can plot the principal components to see the data in 2D

# Plot the results
plt.figure(figsize=(10, 8))
for i, (component1, component2) in enumerate(main_components):
    plt.scatter(component1, component2, label=df['alumno'][i])
    plt.text(component1, component2, df['alumno'][i])

plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.title('PCA - Dos primeras componentes principales')
plt.grid(True)
plt.show()

# We now proceed to calculate the top 3 students based on the first principal component
# We calculate the PCA

pca = PCA(n_components=1)
first_principal_component = pca.fit_transform(normalized_data)

# We create a new dataframe with the first principal component and the student name

df_top_students = pd.DataFrame(
    {'alumno': df['alumno'], 'first_principal_component': first_principal_component.flatten()})

# We sort the dataframe by the first principal component in descending order

df_top_students = df_top_students.sort_values(by='first_principal_component', ascending=False)

# We get the top 3 students
top_students = df_top_students.head(3)

# We log the top 3 students
logger.info("Top 3 estudiantes basados en la primera componente principal:")
logger.info(top_students)

