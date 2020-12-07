# online-hdp
Online inference for the Hierarchical Dirichlet Process. Fits hierarchical Dirichlet process topic models to massive data. The algorithm determines the number of topics. Written by [Chong Wang](http://www.cs.princeton.edu/~chongw/index.html).

## Reference

Chong Wang, John Paisley and David M. Blei. Online variational inference for the hierarchical Dirichlet process. In AISTATS 2011. Oral presentation. [PDF](http://www.cs.princeton.edu/~chongw/papers/WangPaisleyBlei2011.pdf)

## 데이터 준비
- 데이터 준비는 python3 환경에서 실행
- Wikipedia 에서 무작위로 article 퍼오는 코드
- Stream의 개수와 각 stream별로 몇개의 document를 퍼올지에 대해 정해줘야함 : doc, spl 인자
```bash
python Dataloader.py --doc 20 --spl 7
```
이라는 코드는 stream의 개수는 7개이며 각 스트림들은 20개의 document로 구성됨을 뜻함.

## online HDP 실행
- python2 환경에서 실행되어야 함
- 사용되는 인자들은 ```run_online_HDP.py``` 에서 ```parse_args()``` 함수에 설명되어 있음
- 주요 인자로는 ```D, batchsize``` 가 있음
- ```D```는 위에서 정해준 $$doc\times spl$$ 로 정해주고,  ```batchsize```는 위에서 정해준 	```spl```보다 작게 설정해야함

```bash
python run_online_HDP.py --D 140 --batchsize 15
```