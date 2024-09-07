# ikukantai-measurement

## 1. Chuẩn bị các công cụ

+ Latency emulation: `netem`
+ công cụ setup các arch Vanilla và Proposal, tham khảo [setupArch.py](setupArch.py). Ngoài ra cần dev thêm để có thể setup một arch tuỳ ý (ví dụ testcase 2.1)
+ công cụ phát traffic, tham khảo `hey` (easy) và `locust` (difficult), tương lai sẽ chỉ đo bằng `locust`
+ phải thưc hiện được lệnh curl từ node (không curl từ pod, vì curl xong khó lấy kết quả)

## 2. Các testcase cần đo

### 2.0 Lưu ý nhỏ

+ Có 2 Arch chính được mang ra so sánh trong các testcase này là Default Knative và `ikukantai`. Default Knative không thực sự là Knative mặc định, do nó chỉ chạy net-kourier (Gateway) và activator với image mặc định thôi, còn controller chạy image của `ikukantai` =)). Lí do vì sao thì đọc testcase 2.5

### 2.1. Fig.4

#### Ý nghĩa:

Scenario User ở Edge, SNCs được bố trí theo mặc định của Knative (đó là ưu tiên xếp SNC Pod vào các node có nhiều tài nguyên, nên Gateway và Activator ở Cloud), testcase so sánh CDF ResponseTime khi Fx ở Edge và Fx ở Cloud.

Kết quả cho thấy khi Fx ở Cloud cho ResponseTime tệ hơn khi Fx ở Edge, trái với trực giác của người đọc là User ở Edge thì đặt Fx ở Edge sẽ gần hơn, nhanh hơn.

#### Cách dựng:

+ Platform Knative cài image mặc định, tham khảo [patch.sh](utils_cmd\patch.sh) để biết các image mặc định
+ SNC nằm ở Cloud, 1 Gateway và 1 Activator
+ Fx bật 1 pod, [hello.yaml](manifest/demo/hello.yaml) đặt `autoscaling.knative.dev/min-scale: "1"` và `autoscaling.knative.dev/max-scale: "1"`
+ netem 50 ± 10 ms, theo Gauss Distribution, 100Mbps, tham khảo [netem.py](https://github.com/bonavadeur/netemu/blob/master/netem.py)
+ Traffic: `hey -c 1 -q 1 -z 100s http://hello.default.svc.cluster.local`
    + -c 1: 1 cus
    + -q 1: 1 rps
    + -z 100s: phát traffic trong 100s
    + Nên thay phát traffic bằng `hey` sang `locust`

#### Expected result:

Đường Default nằm bên trên đường Edge-Default

### 2.2. Fig.7:

#### Ý nghĩa

So sánh Edge-custom với 2 mô hình trên. Chứng minh được phải đưa SNCs về Edge cùng với Fx thì vấn đề mới được giải quyết. Từ đây dẫn đến ý tưởng thiết kế của `ikukantai` là duplicate hết SNC vào tất cả các node

#### Cách dựng

+ Platform: Default Knative
+ SNCs nằm ở Edge, 1 Gateway 1 Activator
+ 1 Fx
+ Netem 50 ± 10 ms, Gauss Distribution, 100Mbps
+ Traffic: `hey -c 1 -q 1 -z 100s http://hello.default.svc.cluster.local`

#### Expected result:

Đường Edge-Custom tốt hơn hẳn 2 đường còn lại.

### 2.3. Fig.9:

#### Ý nghĩa

Fig.7 Đưa ra ý tưởng thiết kế của `ikukantai` nhưng chưa đủ. Để thực hiện ý tưởng của Edge-Custom chỉ cần modify config của Default Knative chứ không cần modify code. Áp dụng ý tưởng của Edge-Custom để tạo ra 2 Arch là Edge-Duplicate và Cloud-Duplicate. So sánh 4 Arch với nhau.

#### Cách dựng

+ Platform: Default Knative
+ vị trí SNCs:

| Arch | User | Gateway | Activator | Fx |
|-|-|-|-|-|
| Edge-Custom | Edge | 1 Edge | 1 Edge | 1 Edge |
| Edge-Duplicate | Edge | 1 Cloud 1 Edge | 1 Cloud 1 Edge | 1 Cloud 1 Edge |
| Cloud-Duplicate | Cloud | 1 Cloud 1 Edge | 1 Cloud 1 Edge | 1 Cloud 1 Edge |
| Edge-Default | Edge | 1 Cloud | 1 Cloud | 1 Edge |

+ Netem 50 ± 10 ms, Gauss Distribution, 100Mbps
+ Traffic: `hey -c 1 -q 1 -z 100s http://hello.default.svc.cluster.local`
+ Lưu ý các case *-Duplicate thì traffic phải được phát cùng lúc ở 2 nơi Edge và Cloud.

#### Expected result:

Edge-Custom > *-Duplicate > Edge-Default

Cloud-Dup tốt hơn Edge-Dup 1 chút, vì máy ở Cloud mạnh hơn

Edge-Custom và Edge-Dup có vẻ giống nhau về idea nhưng kết quả khác xa nhau  
-> dẫn đến vấn đề về cơ chế LB của Knative làm traffic trong *-Dup đi lộn xộn.  
-> dẫn đến idea thứ 2 của `ikukantai`: sau khi duplicate phải modify lại cơ chế LB

### 2.4. Fig.11:

#### Ý nghĩa

So sánh `ikukantai` và Default Knative

#### Cách dựng

+ Platform:

| Platform | User | Gateway | Activator | Fx |
|-|-|-|-|-|
| `ikukantai` | Edge + Cloud | 1 Master + 1 Cloud + 1 Edge | 1 Master + 1 Cloud + 1 Edge | n Cloud + n Edge |
| Default Knative | Edge + Cloud | 1 Cloud | 1 Cloud | n Cloud + n Edge |

+ Netem latency theo paper, Gauss Distribution, 100Mbps
+ Traffic: theo Paper
+ Lưu ý traffic phải được phát cùng lúc ở 2 nơi Edge và Cloud. Khi viết traffic = 50cus có nghĩa là Edge 50cus, Cloud 50cus, tổng là 100cus
+ giá trị số n:
    + 10cus -> n = 1
    + 50cus -> n = 3
+ Note: Knative có công thức tính số Pod là: số Pod = traffic(cus) / [target](https://github.com/bonavadeur/ikukantai/blob/master/manifest/demo/hello.yaml#L15). Ở đây traffic = 50cus (1 side) tức là tổng traffic = 100cus, target = 10 -> 100/10 = 10 pod -> n lẽ phải bằng 5. Tuy nhiên giá trị n bị phụ thuộc vào [target](https://github.com/bonavadeur/ikukantai/blob/master/manifest/demo/hello.yaml#L15), và thay đổi target không mang lại ý nghĩa gì cho kết quả nên bỏ qua, set n theo hướng dẫn bên trên.

Đọc thêm về target: [Configuring Knative targets](https://knative.dev/docs/serving/autoscaling/autoscaling-targets/#configuring-targets)

#### Expected result:

`ikukantai` tốt hơn hẳn Default Knative

### 2.5. Fig.12 & Fig.13:

#### Ý nghĩa

Một kết quả giải thích cho cơ chế LB của `ikukantai`

#### Cách dựng

+ Platform:
    + Fig.12: Default Knative
    + Fig.13: `ikukantai`

| Platform | User | Gateway | Activator | Fx |
|-|-|-|-|-|
| `ikukantai` | Edge + Cloud | 1 Master + 1 Cloud + 1 Edge | 1 Master + 1 Cloud + 1 Edge | 1 Cloud + 1 Edge |
| Default Knative | Edge + Cloud | 1 Cloud | 1 Cloud | 1 Cloud + 1 Edge |
+ Netem 50 ± 10 ms, Gauss Distribution, 100Mbps
+ Traffic:
    + phát cùng lúc 2 nơi trong 300s,
    + URL: `http://hello.default.svc.cluster.local/nodename`, response trả về sẽ có tên node mà request được serve
    + phát traffic bằng `locust`
    + mỗi side: traffic tăng dần từ 3 -> 50 cus, tham khảo [locust](kien/multi_request/locustfile.py)
+ Lưu ý (tiếp nối lưu ý 2.0):
    + Để response trả về kèm theo tên node (tức là Pod biết nó đang đứng ở node nào), ta dùng [Downward API](https://viblo.asia/p/kubernetes-series-bai-10-downward-api-truy-cap-pod-metadata-m68Z0eGdlkG), truyền vào Pod như một env
    + Mặc định Knative không cho truyền Downward API vào Fx Pod, `ikukantai` được modified source code để tự động truyền tên node vào Pod mà không cần thêm gì vào file [.yaml](https://github.com/bonavadeur/ikukantai/blob/master/manifest/demo/hello.yaml)
    + Code nhận Downward API này của app Hello: [here](https://github.com/bonavadeur/shuka/blob/master/src/app.py#L25), app Hello được build từ image [shuka](https://github.com/bonavadeur/shuka)
    + Thử cài Knative với tất cả các image default, apply hello.yaml, curl URI /nodename sẽ thấy Fx không trả về được tên node
    + Giữ nguyên tất cả các image của default Knative bên trên, thay image controller thành `docker.io/bonavadeur/ikukantai-controller:v1.2-cnsm-15nov24`, test lại.

#### Expected result:

Các chart được vẽ với x-axis là ResponseTime, y-axis là density (bao nhiêu % request vào Cloud, vào Edge)

Khi tăng dần traffic nhưng không tăng số Pod, hiện tượng đầy queue xảy ra, kéo theo ResponseTime tăng. Như vậy data thu được sẽ có ResponseTime biến thiên -> x-axis

Giải thích kết quả:

+ Baseline: Các request được route lẫn lộn giữa Edge và Cloud, nếu được route vào Cloud thì ResponseTime nhìn chung thấp, route vào Edge nhìn chung responseTime cao hơn. Các miền chart:  
    + Đỏ (low): Cloud User -> Gateway -> Activator -> Cloud Fx
    + Đỏ trộn với Xanh (mid):
        + Cloud User -> Gateway -> Activator -> Edge Fx
        + Edge User -> Gateway -> Activator -> Cloud Fx
    + Xanh (high):
        + Edge User -> Gateway -> Activator -> Edge Fx
+ `ikukantai`: request được ưu tiên serving in local do thuật toán LB của `ikukantai`. các phẩn đỏ và xanh trên 50ms thể hiện các request được route tới region khác do local quá tải.

## 3. Épilogue

Khuyến khích vẽ hình trong mỗi case và tự giải thích các kết quả.
