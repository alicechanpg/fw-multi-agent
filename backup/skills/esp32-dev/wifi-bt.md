# ESP32 WiFi / Bluetooth ã|

## WiFi ã|

### WiFi Station !

```c
#include "esp_wifi.h"
#include "esp_event.h"

// À WiFi Station
void wifi_init_sta(void) {
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = "YOUR_SSID",
            .password = "YOUR_PASSWORD",
        },
    };

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());
}
```

### WiFi Event Handler

```c
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                               int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT) {
        switch (event_id) {
            case WIFI_EVENT_STA_START:
                esp_wifi_connect();
                break;
            case WIFI_EVENT_STA_DISCONNECTED:
                esp_wifi_connect();  // Í’Õ#
                break;
        }
    } else if (event_base == IP_EVENT) {
        if (event_id == IP_EVENT_STA_GOT_IP) {
            ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
            ESP_LOGI(TAG, "Got IP: " IPSTR, IP2STR(&event->ip_info.ip));
        }
    }
}
```

## Bluetooth ã|

### BLE GATT Server

```c
#include "esp_bt.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"

// BLE À
void ble_init(void) {
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));
    ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_BLE));
    ESP_ERROR_CHECK(esp_bluedroid_init());
    ESP_ERROR_CHECK(esp_bluedroid_enable());
}
```

### BLE Advertising

```c
static esp_ble_adv_params_t adv_params = {
    .adv_int_min        = 0x20,
    .adv_int_max        = 0x40,
    .adv_type           = ADV_TYPE_IND,
    .own_addr_type      = BLE_ADDR_TYPE_PUBLIC,
    .channel_map        = ADV_CHNL_ALL,
    .adv_filter_policy  = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};

// ãÀ„≠
esp_ble_gap_start_advertising(&adv_params);
```

## 8( Log Pattern

### WiFi #⁄ü
```
I (1234) wifi:connected with SSID, aid = 1, channel 6
I (2345) esp_netif_handlers: sta ip: 192.168.1.100
```

### WiFi #⁄1W
```
W (1234) wifi:sta_state, current state: init, next state: disconnected
E (2345) wifi:sta is connecting, return error
```

### BLE #⁄
```
I (1234) GATTS: ESP_GATTS_CONNECT_EVT, conn_id 0
I (2345) GATTS: ESP_GATTS_MTU_EVT, MTU 517
```

## Troubleshooting

| OL | „zπH |
|------|----------|
| WiFi !’#⁄ | ¢Â SSID/∆º∫ç AP /&(ƒg |
| BLE !’´Éœ0 | ∫ç advertising Ú_’¢Â TX power |
| #⁄iö | øt WiFi power save mode |
