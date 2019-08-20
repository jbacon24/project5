from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Beauty, Base, BeautyItem

engine = create_engine('sqlite:///beautyitems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Items for Makeup
product1 = Beauty(name="Makeup")

session.add(product1)
session.commit()

beautyItem1 = BeautyItem(name="Eye Shadow", description="Cosmetic applied to the eyelid to create depth and dimension",
                     price="$7.50", feature="eyes", product=product1)

session.add(beautyItem1)
session.commit()


beautyItem2 = BeautyItem(name="Lip Gloss", description="Product used to provide a glossy shine and mild color to the lips",
                     price="$2.99", feature="lips", product=product1)

session.add(beautyItem2)
session.commit()

beautyItem3 = BeautyItem(name="Mascara", description="Makeup used to enhance the eyelashes",
                     price="$5.50", feature="eyes", product=product1)

session.add(beautyItem3)
session.commit()

beautyItem4 = BeautyItem(name="Eyeliner", description="Makeup used to emphasize the eyelids and accent the shape of eyes",
                     price="$3.99", feature="eyes", product=product1)

session.add(beautyItem4)
session.commit()

beautyItem5 = BeautyItem(name="Foundation", description="Makeup applied to the face to create an even complexion",
                     price="$7.99", feature="face", product=product1)

session.add(beautyItem5)
session.commit()

beautyItem6 = BeautyItem(name="Blush", description="Makeup applied to the cheeks to add a subtle redness",
                     price="$5.99", feature="face", product=product1)

session.add(beautyItem6)
session.commit()

beautyItem7 = BeautyItem(name="Highlighter", description="Used for contouring, makeup that reflects light and brightens the skin on the applied area",
                     price="$4.99", feature="face", product=product1)

session.add(beautyItem7)
session.commit()

beautyItem8 = BeautyItem(name="Concealer", description="Color correcting makeup used to cover up blemishes, dark spots, aging spots, etc.",
                     price="$3.49", feature="face", product=product1)

session.add(beautyItem8)
session.commit()

beautyItem9 = BeautyItem(name="Primer", description="Base for foundation that allows foundation to appear smoother and last longer",
                     price="$10.99", feature="face", product=product1)

session.add(beautyItem9)
session.commit()


# Items for Skincare
product2 = Beauty(name="Skincare")

session.add(product2)
session.commit()


beautyItem1 = BeautyItem(name="Masks", description="Product used to cleanse, unclog pores, and improve skin appearance",
                     price="$7.99", feature="face", product=product2)

session.add(beautyItem1)
session.commit()

beautyItem2 = BeautyItem(
    name="Makeup Wipes", description="Product used to remove makeup and clean the face", price="$25", feature="Entree", product=product2)

session.add(beautyItem2)
session.commit()

beautyItem3 = BeautyItem(name="Cleansers", description="Facial care product used to remove makeup and other pollutants from the skin",
                     price="15", feature="face", product=product2)

session.add(beautyItem3)
session.commit()

beautyItem4 = BeautyItem(name="Sunscreen", description="Lotion or spray used to protect the skin from UV rays and reduce sunburn",
                     price="12", feature="face", product=product2)

session.add(beautyItem4)
session.commit()

beautyItem5 = BeautyItem(name="Moisturizer", description="Product used to hyradte skin",
                     price="14", feature="face", product=product2)

session.add(beautyItem5)
session.commit()


# Items for Haircare
product3 = Beauty(name="Haircare")

session.add(product3)
session.commit()


beautyItem1 = BeautyItem(name="Shampoo", description="Product used to remove surface debris from scalp and hair",
                     price="$8.99", feature="hair", product=product3)

session.add(beautyItem1)
session.commit()

beautyItem2 = BeautyItem(name="Conditioner", description="Product used to improve the feel and appearance of hair and helps to detangle strands",
                     price="$6.99", feature="hair", product=product3)

session.add(beautyItem2)
session.commit()

beautyItem3 = BeautyItem(name="Hair Spray", description="Styling product used to protect against humity and hold hair in place",
                     price="$9.95", feature="hair", product=product3)

session.add(beautyItem3)
session.commit()

beautyItem4 = BeautyItem(name="Hair Masks", description="Hair treatment to deeply hydrate and nurture hair",
                     price="$6.99", feature="hair", product=product3)

session.add(beautyItem4)
session.commit()


# Items for Bath&Body
product4 = Beauty(name="Bath&Body")

session.add(product4)
session.commit()


beautyItem1 = BeautyItem(name="Exfoliator", description="Product used to remove dead skin cells",
                     price="$2.99", feature="body", product=product4)

session.add(beautyItem1)
session.commit()

beautyItem2 = BeautyItem(name="Body Wash", description="Cleasners used to remove dirt, oil, and other debris from the skin",
                     price="$5.99", feature="body", product=product4)

session.add(beautyItem2)
session.commit()

beautyItem3 = BeautyItem(name="Lotion", description="Product used to smooth and moisturize the skin",
                     price="$4.50", feature="body", product=product4)

session.add(beautyItem3)
session.commit()

beautyItem4 = BeautyItem(name="Deodorant", description="Product used to mask body odor and prevent sweating",
                     price="$6.95", feature="body", product=product4)

session.add(beautyItem4)
session.commit()


print("added beauty products!")
