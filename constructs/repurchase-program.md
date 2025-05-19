---
description: Repurchase Program of the Realm of OGs
---

# ⚙️ Repurchase Program

## On-chain Program

Oggz is an on-chain program deployed on Solana mainnet by the [Institutions](broken-reference) to serve as a balancing mechanism for the flow of [tokens](tokens/), which inevitably accelerates over the Realm's lifespan.

## Program Actions

Oggz serves as the repurchase program that regularly and automatically:

1. Takes possession of SOL collected from both [Mining fees](../institutions/og-mine.md#mining-fees) and [Reserve fees](../institutions/og-reserve.md#reserve-fees) collected each epoch by [OG Mine](../institutions/og-mine.md) and [OG Reserve](../institutions/og-reserve.md), respectively.
2. Uses collected SOL to repurchase both [$OGG](tokens/usdogg-og-gold.md) and [$OGC](tokens/usdogc-og-coin.md) from the open market (via Jupiter routing).
3. Deposits repurchased $OGG and $OGC into OG Mine and OG Reserve, respectively.

## Impact on the Realm

The overall effect of Oggz is to assist in supporting a floor value for [$OGG](tokens/usdogg-og-gold.md) and [$OGC](tokens/usdogc-og-coin.md) by continuously repurchasing these tokens from the open market.&#x20;

Further, this action adds to the daily $OGG epoch reward emitted by the [OG Mine](../institutions/og-mine.md) and extends the tail-end of epochs that the [OG Reserve](../institutions/og-reserve.md) may continue to emit $OGC.

Since repurchases of $OGG and $OGC are routed through Jupiter, the most efficient liquidity path is selected. Therefore, regular repurchases of $OGG and $OGC result in a constant rebalancing of the Realm's [tokens](tokens/), especially for the Realm's most liquid pair of $OGG-$OGC.

## Technical Information

To follow on-chain activity, the Solana public address for Oggz is provided:

{% hint style="info" %}
oggzGFTgRM61YmhEbgWeivVmQx8bSAdBvsPGqN3ZfxN
{% endhint %}
