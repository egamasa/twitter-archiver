# TwitterArchiver

前日1日分のツイート・RT・ふぁぼをTwitter APIから取得し、JSONデータをAmazon S3互換オブジェクトストレージに保存

## Cloud Functions で定期実行

### ソースコードの準備

- **for_cloud_functions** ブランチを Git clone する  
`git clone -b for_cloud_functions https://github.com/egamasa/twitter-archiver.git`

- シークレットの準備  
`secrets.json` に記載
  - Twitter API キー
    - CONSUMER_KEY
    - CONSUMER_SECRET
    - ACCESS_TOKEN
    - ACCESS_TOKEN_SECRET
  - Amazon S3 アクセスキー
    - ACCESS_KEY_ID
    - SECRET_ACCESS_KEY

- 環境変数の準備  
`env.yaml` に記載
  - PROJECT_ID
    - GCP プロジェクトID
  - SECRET_NAME
    - Secret Manager シークレットの名前
  - SECRET_VERSION
    - Secret Manager シークレットのバージョン
      - 新規に登録した場合は `'1'`
  - TOPIC_ID
    - Pub/Sub トピック名
  - ENDPOINT_URL
    - S3 エンドポイント
  - BUCKET_NAME
    - S3 バケット名

- 設定ファイル（出力設定）  
`config.py` に記載
  - SAVE_PATH
    - S3 バケット内でのJSONデータ保存先パス
    - `{yyyy}`→西暦4桁、`{mm}`→月2桁、`{dd}`→日2桁 に置換される
  - SAVE_NAME
    - JSONデータ保存ファイル名
    - `{yyyy}`→西暦4桁、`{mm}`→月2桁、`{dd}`→日2桁 に置換される
    - 拡張子（`.json`）を含めること
  - SAVE_TO_S3
    - S3 バケットへのデータ保存
      - [True]：する／False：しない（ローカルに保存）
  - PUB_TO_IMAGER
    - S3 バケットへのJSONデータ保存後に [TwitterImager](https://github.com/egamasa/twitter-imager) を自動起動  
      （Pub/Sub 経由で TwitterImager へJSONデータのパスを送信し、受信をトリガーとして TwitterImager を起動させる）
      - [True]：する／False：しない
      - **Publish 先**のトピックに Pub/Sub パブリッシャー権限が必要！！

### Secret Manager

- シークレットの登録
  - リージョン指定は任意  
    （Cloud Functions のリージョンに合わせた）

  ```bash
  gcloud secrets create [SECRET (name)] --data-file=secrets.json --locations=asia-northeast1
  ```

- サービスアカウントにシークレット読み取り権限付与

  ```bash
  gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:[SERVICE_ACCOUNT]" --role="roles/secretmanager.secretAccessor"
  ```

### Cloud Pub/Sub

- トピックの作成

  ```bash
  gcloud pubsub topics create [TOPIC_ID]
  ```

### Cloud Functions

- デプロイ
  - リージョン指定は任意  
    （S3互換ストレージのリージョンが東京なので合わせた）

  ```bash
  gcloud functions deploy [NAME] \
    --region asia-northeast1 \
    --entry-point main \
    --memory 256MB \
    --runtime python38 \
    --service-account [SERVICE_ACCOUNT]
    --timeout 90s \
    --env-vars-file env.yaml \
    --trigger-topic [TOPIC_ID]
  ```

- サービスアカウントに関数の権限付与

  ```bash
  gcloud projects add-iam-policy-binding [PROJECT_ID] --member="serviceAccount:[SERVICE_ACCOUNT]" --role="roles/cloudfunctions.serviceAgent"
  ```

### Cloud Scheduler

- cronジョブ作成  
  （毎日、午前0時10分に実行）

  ```bash
  gcloud scheduler jobs create pubsub [JOB (name)] --schedule "10 0 * * *" --topic [TOPIC_ID] --message-body "{}"
  ```

## ローカルで手動実行

### ソースコードの準備

- 設定ファイル  
`config.py` に記載
  - Twitter API キー
    - CONSUMER_KEY
    - CONSUMER_SECRET
    - ACCESS_TOKEN
    - ACCESS_TOKEN_SECRET
  - Amazon S3 アクセスキー
    - ACCESS_KEY_ID
    - SECRET_ACCESS_KEY
  - SAVE_PATH
    - S3 バケット内でのJSONデータ保存先パス
    - `{yyyy}`→西暦4桁、`{mm}`→月2桁、`{dd}`→日2桁 に置換される
  - SAVE_NAME
    - JSONデータ保存ファイル名
    - `{yyyy}`→西暦4桁、`{mm}`→月2桁、`{dd}`→日2桁 に置換される
    - 拡張子（`.json`）を含めること
  - SAVE_TO_S3
    - S3 バケットへのデータ保存
      - [True]：する／False：しない（ローカルに保存）

### パッケージのインストール

```bash
pip install -r requirements.txt
```

### 実行

```bash
python archiver.py
```
