```mermaid
graph LR
    subgraph Presentation Layer [使用者介面層]
        A[主程式] --> B(腳本總覽);
        A --> C(測試進度顯示);
        A --> D(帳號登入介面);
        A --> E(Report列表);
        A --> F(腳本列表);
        A --> G(更新檢查);
        B --> H{腳本資料};
        C --> I{測試進度資料};
        D --> J{使用者帳號};
        E --> K{Report資料};
        F --> L{腳本資料};
        G --> M{版本資訊};
    end

    subgraph Application Logic Layer [應用邏輯層]
        H --> N[腳本解析器];
        I --> O[測試執行引擎];
        J --> P[權限管理];
        K --> Q[Report管理器];
        L --> R[腳本管理器];
        M --> S[自動更新模組];
        N --> O;
        O --> Q;
        R --> N;
        P --> R;
        P --> Q;
        S --> A;
    end

    subgraph Data Layer [資料層]
        H -- 資料庫互動 --> T[腳本資料庫];
        I -- 資料庫互動 --> U[測試紀錄資料庫];
        J -- 資料庫互動 --> V[使用者資料庫];
        K -- 資料庫互動 --> U;
        L -- 資料庫互動 --> T;
        P -- 資料庫互動 --> V;
        R -- 資料庫互動 --> T;
        Q -- 資料庫互動 --> U;
    end

    subgraph External System [外部系統]
        W[硬體自動化系統] <--O--> O;
        X[更新伺服器] <--S--> S;
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style N fill:#ccf,stroke:#333,stroke-width:2px
    style T fill:#eee,stroke:#333,stroke-width:2px
    style W fill:#eec,stroke:#333,stroke-width:2px
    ```