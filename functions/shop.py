class Shop:
    #item shop
    item_shop = {
        "Health Potion": 100,
    }

    #upgrades, 6 levels
    upgrade_shop = {
        "Sharpness Upgrade": [150, 250, 400, 600, 1000, 4000],  # 6 levels, increasing price, line 296, 318. for more levels of upgrade
        "Shield Upgrade": [120, 200, 350, 500, 800]
    }
    # upgrades multiplier (already linked)
    upgrade_multipliers = {
        "Sharpness Upgrade": [1.2, 1.4, 1.7, 2.0, 2.5, 9.0],
        "Shield Upgrade": [1.2, 1.4, 1.7, 2.0, 2.5]
    }
