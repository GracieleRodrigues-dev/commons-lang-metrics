# commons-lang-metrics

### Métricas CK
Para extrair as métricas CK, é necessário:

Clonar o seguinte repositório:

[Repositório CK](https://github.com/mauricioaniche/ck.git)

Rodar o comando dentro da pasta do projeto CK
```js
mvn clean compile package
```

Esse comando irá gerar um .JAR em ``/target/ck-{?}.{?}.{?}-SNAPSHOT-jar-with-dependencies.jar``

Com base no diretório desse arquivo, defina a constante em ck.py
```js
CK_REPO_JAR_DIR="C:/Users/{Username}/Documents/commons-lang-metrics/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"
```

