---
description: Repurchase Programs of the Realm of OGs
---

# ⚙️ Repurchase Programs

## On-chain Programs

The Repurchase Programs are on-chain programs deployed on Solana mainnet by the [Institutions](broken-reference) to serve as a balancing mechanism for the flow of [tokens](tokens/), which inevitably accelerates over the Realm's lifespan.

## Program Actions

There are 3 separate Repurchase Programs that regularly and automatically:

1. Take possession of SOL and [$OGC](tokens/usdogc-og-coin.md) collected from [Mining fees](../institutions/og-mine.md#mining-fees), [Reserve fees](../institutions/og-reserve.md#reserve-fees), and [Lottery fees](../institutions/og-lottery.md#lottery-fees) generated each epoch by [OG Mine](../institutions/og-mine.md), [OG Reserve](../institutions/og-reserve.md), and [OG Lottery](../institutions/og-lottery.md), respectively.
2. Use collected fees to repurchase [$OGG](tokens/usdogg-og-gold.md), [$OGC](tokens/usdogc-og-coin.md), and [$OGF](tokens/usdogf-og-fool.md) from the open market (via Jupiter routing).
3. Deposits repurchased $OGG and $OGC into OG Mine and OG Reserve, respectively.
4. Burns repurchased $OGF.

## Program Comparison

<table><thead><tr><th width="121">Institution</th><th width="78">Token</th><th width="126">Source</th><th width="95" data-type="checkbox">Repurchase</th><th width="83" data-type="checkbox">Replenish</th><th data-type="checkbox">Burned</th><th></th></tr></thead><tbody><tr><td>OG Mine</td><td>$OGG</td><td>Mining fees</td><td>true</td><td>true</td><td>false</td><td>oggzGFTgRM61YmhEbgWeivVmQx8bSAdBvsPGqN3ZfxN</td></tr><tr><td>OG Reserve</td><td>$OGC</td><td>Reserve fees</td><td>true</td><td>true</td><td>false</td><td><p></p><p>9amqn5HuK6554dnAEQWJMMGTyrQBVWzKzt9vdVGTBwKo</p></td></tr><tr><td>OG Lottery</td><td>$OGF</td><td>Lottery fees</td><td>true</td><td>false</td><td>true</td><td>(coming soon)</td></tr></tbody></table>

## Impact on the Realm

The overall effect of the Repurchase Programs is to assist in supporting a floor value for [$OGG](tokens/usdogg-og-gold.md), [$OGC](tokens/usdogc-og-coin.md), and [$OGF](tokens/usdogf-og-fool.md) by continuously repurchasing these tokens from the open market.&#x20;

Further, this action adds to the daily $OGG epoch reward emitted by the [OG Mine](../institutions/og-mine.md) and extends the tail-end of epochs that the [OG Reserve](../institutions/og-reserve.md) may continue to emit $OGC.&#x20;

However, it does not increase emissions or extend the life of[ OG Lottery](../institutions/og-lottery.md). Instead, the Repurchase Program serves to simply decrease excess market supply of $OGF.

Since repurchases of $OGG, $OGC, and $OGF are routed through Jupiter, the most efficient liquidity path is selected. Therefore, regular repurchases of $OGG, $OGC, and $OGF result in a constant rebalancing of the Realm's [tokens](tokens/), especially for the Realm's most liquid pair of $OGG-$OGC, and soon to be $OGC-$OGF.

## Technical Information

To follow on-chain activity, the Solana public address for Oggz is provided:

{% hint style="info" %}
oggzGFTgRM61YmhEbgWeivVmQx8bSAdBvsPGqN3ZfxN
{% endhint %}
