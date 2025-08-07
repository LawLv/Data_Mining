# Data Mining - Assignment 5

Group 51 Chenyang Ding & Yilai Chen

### 1. Implementation of Ja-Be-Ja

#### 1.1 `findPartner`

```java
public Node findPartner(int nodeId, Integer[] nodes) {
    ......
    for (Integer candidate : nodes) {
      Node nodeq = entireGraph.get(candidate);
      //before swap
      int degree_pp = getDegree(nodep, nodep.getColor());
      int degree_qq = getDegree(nodeq, nodeq.getColor());
      double old_weighted_d = Math.pow(degree_pp, config.getAlpha()) + Math.pow(degree_qq, config.getAlpha());
      // assume swap
      int degree_pq = getDegree(nodep, nodeq.getColor());
      int degree_qp = getDegree(nodeq, nodep.getColor());
      double new_weighted_d = Math.pow(degree_pq, config.getAlpha()) + Math.pow(degree_qp, config.getAlpha());
        
      if (annealing) {
        Random random = new Random();
        double prob = random.nextDouble();
        double ann_pro = cal_Ann_Pro(new_weighted_d, old_weighted_d);
        if (new_weighted_d != old_weighted_d && ann_pro > prob && ann_pro > highestBenefit) {
          bestPartner = nodeq;
          highestBenefit = ann_pro;
        }
      } else {
        if (new_weighted_d * T > old_weighted_d && new_weighted_d > highestBenefit) { //Judge by T and benefit
          bestPartner = nodeq;
          highestBenefit = new_weighted_d;
        }
      }
    }
    return bestPartner;
  }
```

First, the same color degree of the current node and the candidate node before and after the exchange is compared, and then a certain probability calculation formula is used to determine whether a suitable partner is found to exchange.

```java
private double cal_Ann_Pro(double new_d, double old_d){
    return Math.exp((new_d - old_d) / Math.pow(T, exponent_round));
  } // T high, P close to 1, tend to accept bad solutions
```

Even if `new_d` is worse than `old_d` (`new_d` - `old_d` < 0), it is still possible to accept the new solution.

When `T` is large, denominator tends to be large, `P` tends to be close to 1, so larger than `prob`.

#### 1.2 `sampleAndSwap`

```java
private void sampleAndSwap(int nodeId) {
    ......
    if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
            || config.getNodeSelectionPolicy() == NodeSelectionPolicy.LOCAL) {
      // TODO swap with random neighbors
      partner = findPartner(nodeId, getNeighbors(nodep));
    }

    if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
            || config.getNodeSelectionPolicy() == NodeSelectionPolicy.RANDOM){
      // TODO if local policy fails then randomly sample the entire graph
      if(partner == null) {
        partner = findPartner(nodeId, getSample(nodeId));
      }
    }
    // TODO swap the colors
    if (partner != null) {
      int tempColor = nodep.getColor();
      nodep.setColor(partner.getColor());
      partner.setColor(tempColor);
      numberOfSwaps++;
    }
  }
```

#### 1.3 `saCoolDown`

```java
private void saCoolDown(){
    // TODO for second task
    if (annealing){
      ......
    }
    else {
      if (T > 1)
        T -= config.getDelta();
      if (T < 1)
        T = 1;
    }
  }
```

- The temperature decreases gradually with each iteration.
- The speed of temperature decrease is controlled by `config.getDelta`(). The larger the delta, the faster the temperature decreases.



### 2. Effect of Simulated Annealing

```java
private int exponent_round = 0;
private int reset_rounds = 0;
private boolean annealing = true;
```

In the initial variable definition, added `exponent_round` to control the exponent adjustment of temperature in the acceptance probability calculation

- `exponent_round` is small (0): the effect of temperature on the acceptance probability is more direct, and annealing is faster.
- `exponent_round` is large: the effect of temperature is slowed down, the annealing speed is slower, and it is more inclined to accept "inferior solutions".
- As the number of rounds increases, the acceptance probability adjustment of the annealing process becomes more and more stringent.

```java
private void saCoolDown(){
    if (annealing){
      exponent_round++;
      T *= config.getDelta();
      if (T < Math.pow(10, -5)) T = (float) Math.pow(10, -5);
      if (T == Math.pow(10, -5)) {
        reset_rounds++;
        if (reset_rounds == 400) {
          T = 1;
          reset_rounds = 0;
          exponent_round = 0;
        }
      }
    }
    else {
      ......
    }
  }
```

