import cv2
import numpy as np
import random
import time
def two_dof_sim_hand(width, height, Q1, Q2, crane1, crane2):
	# width , height: chiều dài, chiều rộng của ảnh, Q1,Q2: góc alpha và beta
	# Crane1,crane2: L1,L2
	# Tạo ảnh đen
	img_crane = np.zeros((height, width, 3), dtype=np.uint8)
	img = np.zeros((height, width, 3), dtype=np.uint8)

	# Khai báo các điểm tay -> từ dưới lên trên O, N, M
	pos_ox, pos_oy = 0, 0
	pos_nx, pos_ny = 0, 0
	pos_mx, pos_my = 0, 0

	# Y phải nhỏ hơn height
	alpha = Q1
	beta = Q2
	# Đổi từ Q độ sang radian
	Q1 = (Q1 * 3.141592) / 180
	Q2 = (Q2 * 3.141592) / 180

	# Hàm tính toán điểm N, M
	pos_nx = crane1 * np.cos(Q1)
	pos_ny = crane1 * np.sin(Q1)

	pos_mx = pos_nx + crane2 * np.cos(Q1+Q2)
	pos_my = pos_ny + crane2 * np.sin(Q1+Q2)

	# Lat hinh 90 do
	temx = [pos_ox,pos_nx,pos_mx]
	temy = [pos_oy,pos_ny,pos_my]
	# lat x
	shift_x = 400
	pos_ox = -temy[0]+shift_x
	pos_nx = -temy[1]+shift_x
	pos_mx = -temy[2]+shift_x
	# lat y
	shift_y = 100
	pos_oy = temx[0]+shift_y
	pos_ny = temx[1]+shift_y
	pos_my = temx[2]+shift_y

	# Vẽ
	# Màu
	rgb1 = [0, 255, 255]
	# Màu 2
	rgb2 = [255, 0, 0]
	# Màu 3
	rgb3 = [255, 221, 0]
	thickness = 2

	# Vẽ cánh tay
	cv2.line(img_crane, (int(pos_ox), int(pos_oy)), (int(pos_nx), int(pos_ny)), (rgb1), thickness)
	cv2.line(img_crane, (int(pos_nx), int(pos_ny)), (int(pos_mx), int(pos_my)), (rgb1), thickness)

	# Vẽ hình tròn đại diện cho bút
	cv2.circle(img_crane, (int(pos_mx), int(pos_my)), 10, (rgb2), -1, 8)

	# Vẽ hình tròn đại diện cho gốc tọa độ
	cv2.circle(img_crane, (int(pos_ox), int(pos_oy)), 10, (rgb2), -1, 8)

	# Thêm văn bản (tên khu vực)
	text_down = 25  # Khoảng cách giữa đỉnh và văn bản

	cv2.putText(img_crane, "Alpha = "+str(alpha), (10, text_down), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (rgb1), 1)
	cv2.putText(img_crane, "Beta = "+str(beta), (int(pos_ox) + 200, text_down), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (rgb1), 1)

	# Gộp ảnh
	img = img + img_crane
	return img_crane

# Example usage:
def main():
	alpha = 0
	beta = 0
	while True:
		#ty le tay va khuuy la 1:0.88
		image = two_dof_sim_hand(800, 500, alpha, beta, 200,176)
		cv2.imshow('2 DOF',image)
		time.sleep(0.1)
		if cv2.waitKey(25) & 0xFF == ord('q'):
			break
		step = 10
		if cv2.waitKey(25) & 0xFF == ord('w'):
			alpha = alpha+step
		if cv2.waitKey(25) & 0xFF == ord('e'):
			beta = beta+step
		if alpha > 0:
			alpha = alpha-5
		if beta > 0:
			beta = beta-5
if __name__=='__main__':
	main()