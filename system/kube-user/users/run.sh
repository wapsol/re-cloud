## docs: https://v1-26.docs.kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/#create-certificatesigningrequest
## docs: https://aungzanbaw.medium.com/a-step-by-step-guide-to-creating-users-in-kubernetes-6a5a2cfd8c71

openssl genpkey -out aliehvo.key -algorithm Ed25519
openssl req -new -key aliehvo.key -out aliehvo.csr -subj "/CN=aliehvo/O=dev"
cat aliehvo.csr | base64 | tr -d "\n"

cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: aliehvo
spec:
  request: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURSBSRVFVRVNULS0tLS0KTUlHZk1GTUNBUUF3SURFUU1BNEdBMVVFQXd3SFlXeHBaV2gyYnpFTU1Bb0dBMVVFQ2d3RFpHVjJNQ293QlFZRApLMlZ3QXlFQXNYakdzdWRJVGdUM0kvbUJwYnZJenNtcm9pM0F0aXh5WWxWVnlUUXhDZWVnQURBRkJnTXJaWEFEClFRRFZhUkZqOHgxYm9mTk91RXhiOUFNZzg2Unhmb0FCQnlIK1p1Uk5XME5ER05yUXpPMUlXUno1RHU0RUdSVmMKOWFnM3ZtNzM1MStjSkQ2R3R6bDQ2cTBNCi0tLS0tRU5EIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLQo=
  signerName: kubernetes.io/kube-apiserver-client
  expirationSeconds: 86400000
  usages:
  - client auth
EOF

kubectl certificate approve aliehvo
kubectl get csr/aliehvo -o jsonpath="{.status.certificate}" | base64 -d > aliehvo.crt
cp ~/.kube/config/config aliehvo-kube-config
kubectl --kubeconfig aliehvo-kube-config config set-credentials aliehvo --client-key aliehvo.key --client-certificate aliehvo.crt --embed-certs=true
kubectl --kubeconfig aliehvo-kube-config config set-context re-cloud-dev --cluster local --user aliehvo


## Bind clusterrole
